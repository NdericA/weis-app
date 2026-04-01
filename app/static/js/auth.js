const USER_STORE_KEY = "weis_users";
const SESSION_STORE_KEY = "weis_session";
let adminRefreshId = null;
let driverReviewRefreshId = null;

const DEFAULT_ADMIN = {
    id: "admin-local-001",
    token: "admin-local-token",
    role: "admin",
    full_name: "WEIS Admin",
    phone_number: "+237699000000",
    email: "admin@weis.cm"
};

function loadUsers() {
    return JSON.parse(localStorage.getItem(USER_STORE_KEY) || "[]");
}

function saveUsers(users) {
    localStorage.setItem(USER_STORE_KEY, JSON.stringify(users));
}

function ensureAdminUser() {
    const users = loadUsers();
    const hasAdmin = users.some((user) => user.role === "admin");
    if (!hasAdmin) {
        users.push(DEFAULT_ADMIN);
        saveUsers(users);
    }
}

function updateUser(mutator) {
    const users = loadUsers();
    const updatedUsers = users.map((user) => mutator({ ...user }));
    saveUsers(updatedUsers);
    return updatedUsers;
}

function getUserById(userId) {
    return loadUsers().find((user) => user.id === userId) || null;
}

async function fetchDriverApplication(phoneNumber) {
    const response = await fetch(`/api/v1/drivers/applications/${encodeURIComponent(phoneNumber)}`);
    if (!response.ok) {
        return null;
    }
    return response.json();
}

function syncLocalDriverFromApplication(application) {
    if (!application) {
        return null;
    }
    const updatedUsers = updateUser((user) => {
        if (user.role === "driver" && user.phone_number === application.phone_number) {
            user.driver_profile = application;
            user.application_status = application.approval_status;
            user.rejection_reason = application.rejection_reason || "";
            user.additional_info_required = application.additional_info_required || false;
            user.additional_info = application.additional_info || "";
        }
        return user;
    });
    return updatedUsers.find((user) => user.role === "driver" && user.phone_number === application.phone_number) || null;
}

function getSession() {
    const session = sessionStorage.getItem(SESSION_STORE_KEY);
    return session ? JSON.parse(session) : null;
}

function saveSession(session) {
    sessionStorage.setItem(SESSION_STORE_KEY, JSON.stringify(session));
}

function logout() {
    sessionStorage.removeItem(SESSION_STORE_KEY);
    window.location.assign("/");
}

function dashboardPathForUser(user) {
    if (!user) {
        return "/login";
    }
    if (user.role === "admin") {
        return "/dashboard/admin";
    }
    if (user.role === "driver") {
        return user.application_status === "approved" ? "/dashboard/driver" : "/dashboard/driver-review";
    }
    return "/dashboard/rider";
}

function parseRoleFromQuery() {
    const params = new URLSearchParams(window.location.search);
    return params.get("role");
}

function redirectIfAuthenticated() {
    const session = getSession();
    if (!session) {
        if (window.location.pathname === "/dashboard" || window.location.pathname.startsWith("/dashboard/")) {
            window.location.href = "/login";
        }
        return;
    }

    const latestUser = getUserById(session.id) || session;
    saveSession(latestUser);

    if (window.location.pathname === "/dashboard") {
        window.location.href = dashboardPathForUser(latestUser);
        return;
    }

    if (window.location.pathname === "/" || window.location.pathname === "/login" || window.location.pathname === "/signup") {
        window.location.href = dashboardPathForUser(latestUser);
    }
}

function toggleDriverSignupFields(role) {
    const driverFields = document.getElementById("driver-signup-fields");
    if (!driverFields) {
        return;
    }
    driverFields.classList.toggle("hidden", role !== "driver");
}

async function handleSignup(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const status = document.getElementById("signup-status");

    const users = loadUsers();
    const exists = users.find((user) => user.phone_number === payload.phone_number && user.role === payload.role);
    if (exists) {
        status.textContent = "An account with that phone number and role already exists. Please log in.";
        return;
    }

    const authResponse = await fetch("/api/v1/auth/register/phone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            phone_number: payload.phone_number,
            full_name: payload.full_name,
            role: payload.role,
            email: payload.email || null
        })
    });
    const authData = await authResponse.json();

    let driverProfile = null;
    if (payload.role === "driver") {
        const driverResponse = await fetch("/api/v1/drivers/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: payload.full_name,
                phone_number: payload.phone_number,
                license_number: payload.license_number,
                national_id_number: payload.national_id_number,
                vehicle_make: payload.vehicle_make,
                vehicle_model: payload.vehicle_model,
                vehicle_color: payload.vehicle_color,
                plate_number: payload.plate_number
            })
        });
        driverProfile = await driverResponse.json();
    }

    const userRecord = {
        id: authData.user_id,
        token: authData.access_token,
        role: payload.role,
        full_name: payload.full_name,
        phone_number: payload.phone_number,
        email: payload.email || "",
        driver_profile: driverProfile,
        application_status: payload.role === "driver" ? "pending" : "approved",
        rejection_reason: "",
        additional_info_required: false,
        additional_info: ""
    };

    users.push(userRecord);
    saveUsers(users);

    if (payload.role === "driver") {
        status.textContent = "Driver application submitted. Wait for admin approval before logging in.";
        form.reset();
        toggleDriverSignupFields("rider");
        return;
    }

    saveSession(userRecord);
    window.location.href = dashboardPathForUser(userRecord);
}

function handleLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const status = document.getElementById("login-status");

    const users = loadUsers();
    const matched = users.find((user) =>
        user.phone_number === payload.phone_number &&
        user.role === payload.role &&
        user.full_name.toLowerCase() === payload.full_name.toLowerCase()
    );

    if (!matched) {
        status.textContent = "Account not found. Check the phone number, role, and full name or create a new account.";
        return;
    }

    if (matched.role === "driver") {
        fetchDriverApplication(matched.phone_number).then((application) => {
            const syncedDriver = application ? (syncLocalDriverFromApplication(application) || matched) : matched;
            saveSession(syncedDriver);
            window.location.href = dashboardPathForUser(syncedDriver);
        });
        return;
    }

    saveSession(matched);
    window.location.href = dashboardPathForUser(matched);
}

function renderAdminDashboard() {
    if (window.location.pathname !== "/dashboard/admin") {
        return;
    }
    const session = getSession();
    if (!session || session.role !== "admin") {
        window.location.href = "/login";
        return;
    }

    fetch("/api/v1/drivers/applications")
        .then((response) => response.json())
        .then((applications) => {
            const pending = applications.filter((user) => user.approval_status === "pending").length;
            const approved = applications.filter((user) => user.approval_status === "approved").length;
            const rejected = applications.filter((user) => user.approval_status === "rejected").length;

            document.getElementById("profile-name").textContent = session.full_name;
            document.getElementById("pending-count").textContent = pending;
            document.getElementById("approved-count").textContent = approved;
            document.getElementById("rejected-count").textContent = rejected;

            const list = document.getElementById("admin-application-list");
            if (applications.length === 0) {
                list.innerHTML = `<div class="empty-block">No driver applications yet.</div>`;
                return;
            }

            list.innerHTML = applications.map((user) => `
        <article class="application-card">
            <div class="application-summary">
                <div>
                    <span class="summary-label">Driver</span>
                    <strong>${user.full_name}</strong>
                    <p class="tip-status">${user.phone_number} · ${user.email || "No email"}</p>
                </div>
                <div>
                    <span class="summary-label">Vehicle</span>
                    <strong>${user.vehicle_summary || "Vehicle pending"}</strong>
                    <p class="tip-status">Status: ${user.approval_status}</p>
                </div>
            </div>
            <div class="application-meta">
                <p class="tip-status">License: ${user.license_number || "N/A"}</p>
                <p class="tip-status">National ID: ${user.national_id_number || "N/A"}</p>
                <p class="tip-status">Additional info: ${user.additional_info || "None provided"}</p>
            </div>
            <div class="application-actions">
                <button type="button" class="button button-dark admin-approve" data-phone="${user.phone_number}">Approve</button>
                <input type="text" class="admin-reason-input" data-phone="${user.phone_number}" placeholder="Rejection reason or required corrections">
                <label class="admin-checkbox">
                    <input type="checkbox" class="admin-info-required" data-phone="${user.phone_number}" ${user.additional_info_required ? "checked" : ""}>
                    Additional info required
                </label>
                <button type="button" class="button button-light danger admin-reject" data-phone="${user.phone_number}">Reject</button>
            </div>
        </article>
    `).join("");

            document.querySelectorAll(".admin-approve").forEach((button) => {
                button.addEventListener("click", async () => {
                    const response = await fetch("/api/v1/drivers/applications/approve", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ phone_number: button.dataset.phone, reason: "", additional_info_required: false })
                    });
                    const updated = await response.json();
                    syncLocalDriverFromApplication(updated);
                    renderAdminDashboard();
                });
            });

            document.querySelectorAll(".admin-reject").forEach((button) => {
                button.addEventListener("click", async () => {
                    const phone = button.dataset.phone;
                    const reasonInput = document.querySelector(`.admin-reason-input[data-phone="${phone}"]`);
                    const infoRequired = document.querySelector(`.admin-info-required[data-phone="${phone}"]`);
                    const reason = reasonInput.value.trim();
                    if (!reason) {
                        reasonInput.focus();
                        return;
                    }
                    const response = await fetch("/api/v1/drivers/applications/reject", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            phone_number: phone,
                            reason,
                            additional_info_required: Boolean(infoRequired.checked)
                        })
                    });
                    const updated = await response.json();
                    syncLocalDriverFromApplication(updated);
                    renderAdminDashboard();
                });
            });
        });
}

function renderDriverReviewDashboard() {
    if (window.location.pathname !== "/dashboard/driver-review") {
        return;
    }
    const session = getSession();
    if (!session || session.role !== "driver") {
        window.location.href = "/login";
        return;
    }

    const localUser = getUserById(session.id) || session;

    const title = document.getElementById("driver-review-title");
    const pill = document.getElementById("driver-review-pill");
    const name = document.getElementById("driver-review-name");
    const copy = document.getElementById("driver-review-copy");
    const rejectionPanel = document.getElementById("driver-rejection-panel");
    const rejectionReason = document.getElementById("driver-rejection-reason");
    const additionalCopy = document.getElementById("driver-additional-copy");
    const additionalForm = document.getElementById("driver-additional-form");
    const additionalStatus = document.getElementById("driver-additional-status");

    fetchDriverApplication(localUser.phone_number).then((application) => {
        const user = application ? (syncLocalDriverFromApplication(application) || localUser) : localUser;
        saveSession(user);
        name.textContent = user.full_name;

        if (user.application_status === "approved") {
            window.location.href = "/dashboard/driver";
            return;
        }

        if (user.application_status === "pending") {
            title.textContent = "Review pending";
            pill.textContent = "Pending";
            pill.className = "status-chip warning";
            copy.textContent = "Your application is under review. Admin will approve or reject it after checking your documents.";
            rejectionPanel.classList.add("hidden");
            additionalForm.classList.add("hidden");
        }

        if (user.application_status === "rejected") {
            title.textContent = "Application rejected";
            pill.textContent = "Rejected";
            pill.className = "status-chip danger";
            copy.textContent = "Your driver application was rejected. Review the reason below.";
            rejectionPanel.classList.remove("hidden");
            rejectionReason.textContent = user.rejection_reason || "No reason provided.";
            additionalCopy.textContent = user.additional_info_required
                ? "Admin requested more details. Submit additional information below."
                : "No extra information was requested.";
            additionalForm.classList.toggle("hidden", !user.additional_info_required);
            if (user.additional_info) {
                document.getElementById("driver-additional-info").value = user.additional_info;
                additionalStatus.textContent = "Your latest additional information is saved and visible to admin.";
            }
        }

        additionalForm?.addEventListener("submit", async (event) => {
            event.preventDefault();
            const infoValue = document.getElementById("driver-additional-info").value.trim();
            const response = await fetch("/api/v1/drivers/applications/additional-info", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    phone_number: user.phone_number,
                    additional_info: infoValue
                })
            });
            const updated = await response.json();
            const refreshedUser = syncLocalDriverFromApplication(updated) || user;
            saveSession(refreshedUser);
            additionalStatus.textContent = "Additional information submitted. Your application is back under review.";
            renderDriverReviewDashboard();
        }, { once: true });
    });
}

function startReviewRefreshLoops() {
    if (window.location.pathname === "/dashboard/admin" && !adminRefreshId) {
        adminRefreshId = window.setInterval(renderAdminDashboard, 1500);
    }
    if (window.location.pathname === "/dashboard/driver-review" && !driverReviewRefreshId) {
        driverReviewRefreshId = window.setInterval(renderDriverReviewDashboard, 1500);
    }
    window.addEventListener("storage", (event) => {
        if (event.key === USER_STORE_KEY) {
            renderDriverReviewDashboard();
        }
    });
}

function hydrateAuthPages() {
    ensureAdminUser();
    redirectIfAuthenticated();

    const signupRole = document.getElementById("signup-role");
    if (signupRole) {
        const presetRole = parseRoleFromQuery();
        if (presetRole === "rider" || presetRole === "driver") {
            signupRole.value = presetRole;
        }
        toggleDriverSignupFields(signupRole.value);
        signupRole.addEventListener("change", (event) => toggleDriverSignupFields(event.target.value));
    }

    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", handleSignup);
    }

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    const logoutButton = document.getElementById("logout-button");
    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }

    renderAdminDashboard();
    renderDriverReviewDashboard();
    startReviewRefreshLoops();
}

window.WEISAuth = {
    logout
};

hydrateAuthPages();
