const USER_STORE_KEY = "weis_users";
const SESSION_STORE_KEY = "weis_session";

function loadUsers() {
    return JSON.parse(localStorage.getItem(USER_STORE_KEY) || "[]");
}

function saveUsers(users) {
    localStorage.setItem(USER_STORE_KEY, JSON.stringify(users));
}

function getSession() {
    const session = sessionStorage.getItem(SESSION_STORE_KEY);
    if (session) {
        return JSON.parse(session);
    }
    const legacySession = localStorage.getItem(SESSION_STORE_KEY);
    if (legacySession) {
        sessionStorage.setItem(SESSION_STORE_KEY, legacySession);
        localStorage.removeItem(SESSION_STORE_KEY);
        return JSON.parse(legacySession);
    }
    return null;
}

function saveSession(session) {
    sessionStorage.setItem(SESSION_STORE_KEY, JSON.stringify(session));
}

function logout() {
    sessionStorage.removeItem(SESSION_STORE_KEY);
    window.location.assign("/");
}

function dashboardPath(role) {
    return role === "driver" ? "/dashboard/driver" : "/dashboard/rider";
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
    if (window.location.pathname === "/dashboard") {
        window.location.href = dashboardPath(session.role);
        return;
    }
    if (window.location.pathname === "/" || window.location.pathname === "/login" || window.location.pathname === "/signup") {
        window.location.href = dashboardPath(session.role);
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
        driver_profile: driverProfile
    };
    users.push(userRecord);
    saveUsers(users);
    saveSession(userRecord);
    window.location.href = dashboardPath(userRecord.role);
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

    saveSession(matched);
    window.location.href = dashboardPath(matched.role);
}

function hydrateAuthPages() {
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
}

window.WEISAuth = {
    logout
};

hydrateAuthPages();
