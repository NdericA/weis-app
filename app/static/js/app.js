const estimateButton = document.getElementById("estimate-button");
const bookingForm = document.getElementById("booking-form");
const refreshPricingButton = document.getElementById("refresh-pricing");
const toggleDriverStatusButton = document.getElementById("toggle-driver-status");
const acceptRideButton = document.getElementById("accept-ride");
const declineRideButton = document.getElementById("decline-ride");
const arrivedTripButton = document.getElementById("arrived-trip");
const startTripButton = document.getElementById("start-trip");
const completeTripButton = document.getElementById("complete-trip");
const tipButtons = Array.from(document.querySelectorAll(".tip-button"));
const confirmTipButton = document.getElementById("confirm-tip-button");
const applyCustomTipButton = document.getElementById("apply-custom-tip");
const customTipInput = document.getElementById("custom-tip-input");
const replyButtons = Array.from(document.querySelectorAll(".reply-button"));
const sendDriverReplyButton = document.getElementById("send-driver-reply");
const driverReplyInput = document.getElementById("driver-reply-input");
const logoutButton = document.getElementById("logout-button");
const languageToggle = document.getElementById("language-toggle");
const riderChatInput = document.getElementById("rider-chat-input");
const sendRiderMessageButton = document.getElementById("send-rider-message");
const driverChatInput = document.getElementById("driver-chat-input");
const sendDriverMessageButton = document.getElementById("send-driver-message");

const DEFAULT_POSITIONS = {
    riderPosition: { x: 22, y: 62 },
    pickupPosition: { x: 22, y: 62 },
    dropoffPosition: { x: 78, y: 28 },
    driverPosition: { x: 78, y: 76 }
};

const state = {
    driverAvailability: "online",
    estimate: null,
    request: null,
    trip: null,
    messages: [],
    arrivalReady: false,
    selectedTipAmount: null,
    confirmedTipAmount: null,
    driverBaseTotal: 28500,
    driverRunningTotal: 28500,
    driverReplyDraft: "",
    driverReplySent: "",
    riderPosition: { ...DEFAULT_POSITIONS.riderPosition },
    pickupPosition: { ...DEFAULT_POSITIONS.pickupPosition },
    dropoffPosition: { ...DEFAULT_POSITIONS.dropoffPosition },
    driverPosition: { ...DEFAULT_POSITIONS.driverPosition },
    pollingId: null,
    language: localStorage.getItem("weis_language") || "en"
};

function $(id) {
    return document.getElementById(id);
}

function hasElement(id) {
    return Boolean($(id));
}

function getSession() {
    const session = sessionStorage.getItem("weis_session");
    return session ? JSON.parse(session) : null;
}

const translations = {
    en: {
        dashboardRider: "Rider dashboard",
        dashboardDriver: "Driver dashboard",
        language: "Language",
        riderRequestTitle: "Request a ride",
        driverCommandCenter: "Driver command center",
        riderChatTitle: "Chat with driver",
        driverChatTitle: "Chat with rider",
        riderChatPlaceholder: "Message your driver before pickup",
        driverChatPlaceholder: "Message the rider before pickup",
        send: "Send",
        estimate: "Estimate fare",
        requestRide: "Request ride",
        arrived: "Arrived",
        startTrip: "Start trip",
        completeTrip: "Complete trip",
        toggleAvailability: "Toggle availability",
        logout: "Logout"
    },
    fr: {
        dashboardRider: "Tableau de bord passager",
        dashboardDriver: "Tableau de bord chauffeur",
        language: "Langue",
        riderRequestTitle: "Demander une course",
        driverCommandCenter: "Centre de commande chauffeur",
        riderChatTitle: "Discussion avec le chauffeur",
        driverChatTitle: "Discussion avec le passager",
        riderChatPlaceholder: "Envoyez un message au chauffeur avant la prise en charge",
        driverChatPlaceholder: "Envoyez un message au passager avant la prise en charge",
        send: "Envoyer",
        estimate: "Estimer le tarif",
        requestRide: "Demander la course",
        arrived: "Arrive",
        startTrip: "Commencer la course",
        completeTrip: "Terminer la course",
        toggleAvailability: "Changer la disponibilite",
        logout: "Se deconnecter"
    }
};

function requireSession() {
    if (!window.location.pathname.startsWith("/dashboard")) {
        return null;
    }
    const currentSession = getSession();
    if (!currentSession) {
        window.location.href = "/login";
        return null;
    }
    return currentSession;
}

const session = requireSession();

function bookingPayload() {
    if (!bookingForm) {
        return {};
    }
    const formData = new FormData(bookingForm);
    return Object.fromEntries(formData.entries());
}

function formatMoney(value) {
    return `XAF ${Number(value || 0).toLocaleString()}`;
}

function setText(id, value) {
    const element = $(id);
    if (element) {
        element.textContent = value;
    }
}

function distanceKm(a, b) {
    const dx = Number(a.x) - Number(b.x);
    const dy = Number(a.y) - Number(b.y);
    return (Math.sqrt((dx * dx) + (dy * dy)) / 8.5).toFixed(1);
}

function setChip(id, label, variant) {
    const element = $(id);
    if (!element) {
        return;
    }
    element.textContent = label;
    element.className = `status-chip ${variant}`;
}

function placePin(id, position, visible = true) {
    const element = $(id);
    if (!element || !position) {
        return;
    }
    element.style.left = `${position.x}%`;
    element.style.top = `${position.y}%`;
    element.classList.toggle("hidden", !visible);
}

function normalizeTrip(rawTrip) {
    if (!rawTrip) {
        return null;
    }
    return {
        tripId: rawTrip.tripId || rawTrip.trip_id,
        driverId: rawTrip.driverId || rawTrip.driver_id,
        driverUserId: rawTrip.driverUserId || rawTrip.driver_user_id,
        driverName: rawTrip.driverName || rawTrip.driver_name,
        vehicleSummary: rawTrip.vehicleSummary || rawTrip.vehicle_summary,
        paymentMethod: rawTrip.paymentMethod || rawTrip.payment_method,
        baseFare: Number(rawTrip.baseFare ?? rawTrip.base_fare ?? 0),
        stage: rawTrip.stage,
        stageLabel: rawTrip.stageLabel || rawTrip.stage_label
    };
}

function normalizeEstimate(rawEstimate) {
    if (!rawEstimate) {
        return null;
    }
    return {
        currency_code: rawEstimate.currency_code || "XAF",
        ride_type: rawEstimate.ride_type,
        estimated_fare: Number(rawEstimate.estimated_fare ?? 0),
        base_fare: Number(rawEstimate.base_fare ?? 0),
        distance_fare: Number(rawEstimate.distance_fare ?? 0),
        time_fare: Number(rawEstimate.time_fare ?? 0),
        surge_multiplier: Number(rawEstimate.surge_multiplier ?? 1)
    };
}

function applyLiveState(liveState) {
    state.driverAvailability = session && session.role === "driver"
        ? liveState.driver_statuses?.[session.id] || "online"
        : state.driverAvailability;
    state.estimate = normalizeEstimate(liveState.estimate);
    state.request = liveState.request;
    state.trip = normalizeTrip(liveState.trip);
    state.messages = liveState.messages || [];
    state.arrivalReady = Boolean(liveState.arrival_ready);
    if (liveState.selected_tip_amount !== null) {
        state.selectedTipAmount = Number(liveState.selected_tip_amount);
    } else if (!state.trip || state.trip.stage !== "completed") {
        state.selectedTipAmount = null;
    }
    state.confirmedTipAmount = liveState.confirmed_tip_amount === null ? null : Number(liveState.confirmed_tip_amount);
    state.driverReplySent = liveState.driver_reply_sent || "";
    state.driverBaseTotal = Number(liveState.driver_base_total ?? state.driverBaseTotal);
    state.driverRunningTotal = Number(liveState.driver_running_total ?? state.driverRunningTotal);
    state.riderPosition = liveState.rider_position || { ...DEFAULT_POSITIONS.riderPosition };
    state.pickupPosition = liveState.pickup_position || { ...DEFAULT_POSITIONS.pickupPosition };
    state.dropoffPosition = liveState.dropoff_position || { ...DEFAULT_POSITIONS.dropoffPosition };
    state.driverPosition = liveState.driver_position || { ...DEFAULT_POSITIONS.driverPosition };
}

async function liveRequest(path, payload = null, method = "POST") {
    const options = {
        method,
        headers: { "Content-Type": "application/json" }
    };
    if (payload !== null) {
        options.body = JSON.stringify(payload);
    }
    const response = await fetch(`/api/v1/live/${path}`, options);
    if (!response.ok) {
        throw new Error(`live-request-failed:${path}`);
    }
    return response.json();
}

async function fetchLiveState() {
    const response = await fetch("/api/v1/live/state");
    if (!response.ok) {
        throw new Error("live-state-failed");
    }
    const liveState = await response.json();
    applyLiveState(liveState);
    renderAll();
    return liveState;
}

function calculateLocalEstimate(payload) {
    const baseFare = 1000;
    const distanceFare = Number(payload.distance_km) * 225;
    const timeFare = Number(payload.duration_minutes) * 45;
    const estimatedFare = Math.max(baseFare + distanceFare + timeFare, 1500);
    return {
        currency_code: "XAF",
        ride_type: payload.ride_type,
        estimated_fare: estimatedFare,
        base_fare: baseFare,
        distance_fare: distanceFare,
        time_fare: timeFare,
        surge_multiplier: 1.0
    };
}

function currentDriverVehicle() {
    if (!session || session.role !== "driver") {
        return "Vehicle pending";
    }
    return session.driver_profile?.vehicle_summary || "Vehicle pending";
}

function isAssignedDriver() {
    return Boolean(session && session.role === "driver" && state.trip && state.trip.driverUserId === session.id);
}

function hydrateDashboardIdentity() {
    if (!session) {
        return;
    }

    const roleLabel = session.role === "driver" ? "Driver" : "Rider";
    const currentPath = window.location.pathname;
    if (currentPath === "/dashboard/rider" && session.role !== "rider") {
        window.location.href = "/dashboard/driver";
        return;
    }
    if (currentPath === "/dashboard/driver" && session.role !== "driver") {
        window.location.href = "/dashboard/rider";
        return;
    }

    if (hasElement("profile-name")) $("profile-name").textContent = session.full_name;
    if (hasElement("profile-role")) $("profile-role").textContent = roleLabel;
    if (hasElement("dashboard-title")) $("dashboard-title").textContent = `${roleLabel} dashboard`;
    if (hasElement("hero-kicker")) $("hero-kicker").textContent = roleLabel === "Driver" ? "Driver workspace" : "Rider workspace";
    if (hasElement("hero-headline")) {
        $("hero-headline").textContent = roleLabel === "Driver"
            ? "Manage requests, complete trips, and track earnings."
            : "Request rides, track your driver, and settle trips.";
    }
    if (hasElement("hero-copy")) {
        $("hero-copy").textContent = roleLabel === "Driver"
            ? "This dashboard is tailored to the driver workflow, including availability, earnings, tipping, and rider replies."
            : "This dashboard is tailored to the rider workflow, including booking, live tracking, trip completion, and tipping.";
    }
    if (hasElement("hero-role-card")) $("hero-role-card").textContent = roleLabel;
    if (hasElement("hero-phone-card")) $("hero-phone-card").textContent = session.phone_number;
    if (session.role === "rider" && hasElement("rider-id-input")) $("rider-id-input").value = session.id;
    if (session.role === "driver" && hasElement("driver-name-card")) $("driver-name-card").textContent = session.full_name;
    if (session.role === "driver" && hasElement("driver-vehicle-card")) $("driver-vehicle-card").textContent = currentDriverVehicle();
}

function translate(key) {
    return translations[state.language]?.[key] || translations.en[key] || key;
}

function applyLanguage() {
    document.documentElement.lang = state.language;
    setText("language-label", translate("language"));
    if (session?.role === "rider") {
        setText("dashboard-title", translate("dashboardRider"));
    }
    if (session?.role === "driver") {
        setText("dashboard-title", translate("dashboardDriver"));
    }
    const riderPanelTitle = document.querySelector("#rider-panel .panel-header h3");
    if (riderPanelTitle) {
        riderPanelTitle.textContent = translate("riderRequestTitle");
    }
    const driverPanelTitle = document.querySelector("#driver-panel .panel-header h3");
    if (driverPanelTitle) {
        driverPanelTitle.textContent = translate("driverCommandCenter");
    }
    setText("chat-title", session?.role === "driver" ? translate("driverChatTitle") : translate("riderChatTitle"));
    if (riderChatInput) riderChatInput.placeholder = translate("riderChatPlaceholder");
    if (driverChatInput) driverChatInput.placeholder = translate("driverChatPlaceholder");
    if (sendRiderMessageButton) sendRiderMessageButton.textContent = translate("send");
    if (sendDriverMessageButton) sendDriverMessageButton.textContent = translate("send");
    if (estimateButton) estimateButton.textContent = translate("estimate");
    if (bookingForm) bookingForm.querySelector("button[type='submit']").textContent = translate("requestRide");
    if (arrivedTripButton) arrivedTripButton.textContent = translate("arrived");
    if (startTripButton) startTripButton.textContent = translate("startTrip");
    if (completeTripButton) completeTripButton.textContent = translate("completeTrip");
    if (toggleDriverStatusButton) toggleDriverStatusButton.textContent = translate("toggleAvailability");
    if (logoutButton) logoutButton.textContent = translate("logout");
}

function messagingEnabled() {
    return Boolean(state.request || (state.trip && ["accepted", "driver_arrived"].includes(state.trip.stage)));
}

function renderChat() {
    const chatLog = session?.role === "driver" ? $("driver-chat-log") : $("rider-chat-log");
    const chatPanel = session?.role === "driver" ? null : $("rider-chat-panel");
    if (!chatLog) {
        return;
    }
    if (chatPanel && chatPanel.id === "rider-chat-panel") {
        chatPanel.classList.toggle("hidden", !messagingEnabled());
    }
    if (!messagingEnabled()) {
        chatLog.innerHTML = `<div class="chat-empty">${state.language === "fr" ? "La messagerie est disponible entre la demande et la prise en charge." : "Messaging is available from request until pickup."}</div>`;
        if (sendRiderMessageButton) sendRiderMessageButton.disabled = true;
        if (sendDriverMessageButton) sendDriverMessageButton.disabled = true;
        return;
    }
    if (state.messages.length === 0) {
        chatLog.innerHTML = `<div class="chat-empty">${state.language === "fr" ? "Aucun message pour le moment." : "No messages yet."}</div>`;
    } else {
        chatLog.innerHTML = state.messages.map((entry) => `
            <div class="chat-message ${entry.sender_id === session?.id ? "self" : ""}">
                <strong>${entry.sender_name}</strong>
                <span>${entry.message}</span>
            </div>
        `).join("");
        chatLog.scrollTop = chatLog.scrollHeight;
    }
    if (sendRiderMessageButton) sendRiderMessageButton.disabled = !riderChatInput.value.trim();
    if (sendDriverMessageButton) sendDriverMessageButton.disabled = !driverChatInput.value.trim();
}

function drawRouteLine() {
    if (!hasElement("route-line")) {
        return;
    }
    const route = $("route-line");
    if ((!state.request && !state.trip) || (state.trip && state.trip.stage === "completed")) {
        route.classList.add("hidden");
        return;
    }

    const driver = state.driverPosition;
    const target = state.trip && state.trip.stage === "on_trip" ? state.dropoffPosition : state.pickupPosition;
    const deltaX = target.x - driver.x;
    const deltaY = target.y - driver.y;
    const length = Math.sqrt((deltaX * deltaX) + (deltaY * deltaY));
    const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

    route.classList.remove("hidden");
    route.style.left = `${driver.x}%`;
    route.style.top = `${driver.y}%`;
    route.style.width = `${length}%`;
    route.style.transform = `rotate(${angle}deg)`;
}

function renderEstimate() {
    if (!hasElement("estimate-total")) {
        return;
    }
    if (!state.estimate) {
        $("estimate-total").textContent = "XAF -";
        $("estimate-breakdown").textContent = "Use Estimate fare to calculate the trip price.";
        return;
    }

    $("estimate-total").textContent = formatMoney(state.estimate.estimated_fare);
    $("estimate-breakdown").textContent = `Base ${formatMoney(state.estimate.base_fare)}, distance ${formatMoney(state.estimate.distance_fare)}, time ${formatMoney(state.estimate.time_fare)}.`;
}

function renderRiderProgress(currentStage) {
    const steps = document.querySelectorAll(".progress-step");
    if (steps.length === 0) {
        return;
    }
    const stepOrder = ["requested", "accepted", "driver_arrived", "on_trip", "completed"];
    const currentIndex = currentStage ? stepOrder.indexOf(currentStage) : -1;
    steps.forEach((step) => {
        const stepName = step.dataset.step;
        const stepIndex = stepOrder.indexOf(stepName);
        step.classList.toggle("active", stepIndex !== -1 && stepIndex <= currentIndex);
        step.classList.toggle("current", stepName === currentStage);
    });
}

function renderRider() {
    if (!hasElement("rider-status-pill")) {
        return;
    }

    const tipPanel = $("tip-panel");
    const tipStatus = $("tip-status");
    const riderReplyBox = $("rider-reply-box");
    const riderDriverInfo = $("rider-driver-info");
    const riderProgressPanel = $("rider-progress-panel");

    if (!state.request && !state.trip) {
        setChip("rider-status-pill", "Idle", "neutral");
        $("rider-request-state").textContent = "No active request";
        $("rider-request-copy").textContent = "When a request is live, assignment updates appear here.";
        $("rider-distance-live").textContent = "-";
        $("rider-distance-copy").textContent = "Driver distance to pickup updates in real time.";
        tipPanel.classList.add("hidden");
        riderReplyBox.classList.add("hidden");
        riderDriverInfo.classList.add("hidden");
        riderProgressPanel.classList.add("hidden");
        if (confirmTipButton) confirmTipButton.disabled = true;
        tipStatus.textContent = "Tips are optional and only appear after trip completion.";
        renderRiderProgress(null);
        return;
    }

    if (state.request && !state.trip) {
        setChip("rider-status-pill", "Searching", "warning");
        $("rider-request-state").textContent = "Ride requested";
        $("rider-request-copy").textContent = "Your request is live and visible to online drivers.";
        $("rider-distance-live").textContent = `${distanceKm(state.driverPosition, state.pickupPosition)} km`;
        $("rider-distance-copy").textContent = "The closest online driver distance is shown here.";
        tipPanel.classList.add("hidden");
        riderReplyBox.classList.add("hidden");
        riderDriverInfo.classList.add("hidden");
        riderProgressPanel.classList.remove("hidden");
        if (confirmTipButton) confirmTipButton.disabled = true;
        renderRiderProgress("requested");
        return;
    }

    const riderStageCopy = {
        accepted: "A driver accepted your ride and is heading to pickup.",
        driver_arrived: "Your driver has arrived at the pickup location.",
        on_trip: "Your trip is in progress.",
        completed: "Your trip is complete. You can tip the driver now."
    };
    const distanceText = state.trip.stage === "on_trip"
        ? `${distanceKm(state.driverPosition, state.dropoffPosition)} km to destination`
        : `${distanceKm(state.driverPosition, state.pickupPosition)} km to pickup`;

    setChip("rider-status-pill", state.trip.stageLabel, state.trip.stage === "completed" ? "success" : "info");
    $("rider-request-state").textContent = state.trip.stageLabel;
    $("rider-request-copy").textContent = riderStageCopy[state.trip.stage] || "Trip status updated.";
    $("rider-distance-live").textContent = distanceText;
    $("rider-distance-copy").textContent = "Live trip progress updates as the driver changes trip status.";
    riderDriverInfo.classList.remove("hidden");
    riderProgressPanel.classList.remove("hidden");
    $("rider-driver-name").textContent = state.trip.driverName || "Assigned driver";
    $("rider-driver-vehicle").textContent = state.trip.vehicleSummary || "Vehicle details pending";
    renderRiderProgress(state.trip.stage);

    if (state.trip.stage === "completed") {
        tipPanel.classList.remove("hidden");
        if (confirmTipButton) {
            confirmTipButton.disabled = state.confirmedTipAmount !== null || state.selectedTipAmount === null;
        }
        tipButtons.forEach((button) => {
            button.classList.toggle("active", Number(button.dataset.tip) === Number(state.selectedTipAmount));
        });
        tipStatus.textContent = state.confirmedTipAmount === null
            ? state.selectedTipAmount === null
                ? "Select a preset or custom amount, then confirm the tip."
                : `Selected amount: ${formatMoney(state.selectedTipAmount)}. Confirm to send it to the driver.`
            : state.confirmedTipAmount === 0
                ? "No tip added. Trip closed."
                : `Tip confirmed: ${formatMoney(state.confirmedTipAmount)}. The driver received it.`;
        if (state.driverReplySent) {
            riderReplyBox.classList.remove("hidden");
            $("rider-reply-message").textContent = state.driverReplySent;
        } else {
            riderReplyBox.classList.add("hidden");
        }
    } else {
        tipPanel.classList.add("hidden");
        riderReplyBox.classList.add("hidden");
        if (confirmTipButton) confirmTipButton.disabled = true;
        tipButtons.forEach((button) => button.classList.remove("active"));
    }
}

function renderDriverRequest() {
    if (!hasElement("driver-request-box")) {
        return;
    }
    const requestBox = $("driver-request-box");
    const isAvailable = state.driverAvailability === "online";
    setChip("driver-status-pill", isAvailable ? "Online" : "Paused", isAvailable ? "success" : "warning");

    if (!session || session.role !== "driver") {
        requestBox.className = "empty-block";
        requestBox.textContent = "Driver login required.";
        if (acceptRideButton) acceptRideButton.disabled = true;
        if (declineRideButton) declineRideButton.disabled = true;
        return;
    }

    if (!state.request && state.trip && !isAssignedDriver()) {
        requestBox.className = "empty-block";
        requestBox.textContent = `${state.trip.driverName || "Another driver"} has already accepted this ride.`;
        if (acceptRideButton) acceptRideButton.disabled = true;
        if (declineRideButton) declineRideButton.disabled = true;
        return;
    }

    if (!state.request || !isAvailable) {
        requestBox.className = "empty-block";
        requestBox.textContent = isAvailable
            ? "No ride is waiting. Ask the rider to submit a request."
            : "Driver is paused and will not receive new requests.";
        if (acceptRideButton) acceptRideButton.disabled = true;
        if (declineRideButton) declineRideButton.disabled = true;
        return;
    }

    requestBox.className = "request-summary";
    requestBox.innerHTML = `
        <div>
            <span class="summary-label">Rider</span>
            <strong>${state.request.rider_name}</strong>
        </div>
        <div>
            <span class="summary-label">Pickup</span>
            <strong>${state.request.pickup_address}</strong>
        </div>
        <div>
            <span class="summary-label">Destination</span>
            <strong>${state.request.destination_address}</strong>
        </div>
        <div>
            <span class="summary-label">Estimated fare</span>
            <strong>${formatMoney(state.request.estimated_fare)}</strong>
        </div>
    `;
    if (acceptRideButton) acceptRideButton.disabled = false;
    if (declineRideButton) declineRideButton.disabled = false;
}

function renderDriverTrip() {
    if (!hasElement("driver-trip-box")) {
        return;
    }
    const tripBox = $("driver-trip-box");
    if (!state.trip) {
        tripBox.className = "empty-block";
        tripBox.textContent = "Accept a ride to unlock trip controls.";
        if (arrivedTripButton) arrivedTripButton.disabled = true;
        if (startTripButton) startTripButton.disabled = true;
        if (completeTripButton) completeTripButton.disabled = true;
        return;
    }

    if (!isAssignedDriver()) {
        tripBox.className = "empty-block";
        tripBox.textContent = `${state.trip.driverName || "Another driver"} is handling this trip.`;
        if (arrivedTripButton) arrivedTripButton.disabled = true;
        if (startTripButton) startTripButton.disabled = true;
        if (completeTripButton) completeTripButton.disabled = true;
        return;
    }

    const distanceText = state.trip.stage === "on_trip"
        ? `${distanceKm(state.driverPosition, state.dropoffPosition)} km remaining`
        : `${distanceKm(state.driverPosition, state.pickupPosition)} km to pickup`;

    tripBox.className = "request-summary";
    tripBox.innerHTML = `
        <div>
            <span class="summary-label">Trip ID</span>
            <strong>${state.trip.tripId}</strong>
        </div>
        <div>
            <span class="summary-label">Stage</span>
            <strong>${state.trip.stageLabel}</strong>
        </div>
        <div>
            <span class="summary-label">Distance</span>
            <strong>${distanceText}</strong>
        </div>
        <div>
            <span class="summary-label">Payment</span>
            <strong>${state.trip.paymentMethod}</strong>
        </div>
    `;

    if (arrivedTripButton) arrivedTripButton.disabled = !(state.trip.stage === "accepted" && state.arrivalReady);
    if (startTripButton) startTripButton.disabled = state.trip.stage !== "driver_arrived";
    if (completeTripButton) completeTripButton.disabled = state.trip.stage !== "on_trip";
}

function renderDriverEarnings() {
    if (!hasElement("driver-earnings-box")) {
        return;
    }
    $("driver-total-earnings").textContent = formatMoney(state.driverRunningTotal);
    const box = $("driver-earnings-box");

    if (!state.trip || !isAssignedDriver()) {
        $("driver-total-copy").textContent = "Base total before the current live trip settles.";
        box.innerHTML = `
            <div>
                <span class="summary-label">Base trip</span>
                <strong>XAF -</strong>
            </div>
            <div>
                <span class="summary-label">Tip</span>
                <strong>XAF -</strong>
            </div>
            <div>
                <span class="summary-label">Trip total</span>
                <strong>XAF -</strong>
            </div>
            <div>
                <span class="summary-label">Running total</span>
                <strong>${formatMoney(state.driverRunningTotal)}</strong>
            </div>
        `;
        return;
    }

    const baseTrip = Number(state.trip.baseFare ?? 0);
    const confirmedTip = Number(state.confirmedTipAmount ?? 0);
    const currentTripTotal = baseTrip + confirmedTip;
    $("driver-total-copy").textContent = confirmedTip > 0
        ? `This trip includes a confirmed tip of ${formatMoney(confirmedTip)}.`
        : "The live trip total updates here, including tips once confirmed.";
    box.innerHTML = `
        <div>
            <span class="summary-label">Base trip</span>
            <strong>${formatMoney(baseTrip)}</strong>
        </div>
        <div>
            <span class="summary-label">Tip</span>
            <strong>${formatMoney(confirmedTip)}</strong>
        </div>
        <div>
            <span class="summary-label">Trip total</span>
            <strong>${formatMoney(currentTripTotal)}</strong>
        </div>
        <div>
            <span class="summary-label">Running total</span>
            <strong>${formatMoney(state.driverRunningTotal)}</strong>
        </div>
    `;
}

function renderDriverReply() {
    if (!hasElement("driver-thanks-box")) {
        return;
    }
    const box = $("driver-thanks-box");
    const canReply = Boolean(isAssignedDriver() && state.trip && state.trip.stage === "completed" && state.confirmedTipAmount !== null);
    if (sendDriverReplyButton) {
        sendDriverReplyButton.disabled = !canReply || !driverReplyInput.value.trim();
    }

    if (!canReply) {
        box.className = "empty-block";
        box.textContent = "Tip confirmation from the rider unlocks a thank-you reply.";
        return;
    }

    if (state.driverReplySent) {
        box.className = "request-summary compact-summary";
        box.innerHTML = `
            <div>
                <span class="summary-label">Tip received</span>
                <strong>${formatMoney(state.confirmedTipAmount)}</strong>
            </div>
            <div>
                <span class="summary-label">Reply sent</span>
                <strong>${state.driverReplySent}</strong>
            </div>
        `;
        return;
    }

    box.className = "request-summary compact-summary";
    box.innerHTML = `
        <div>
            <span class="summary-label">Trip total</span>
            <strong>${formatMoney(Number(state.trip.baseFare ?? 0) + Number(state.confirmedTipAmount ?? 0))}</strong>
        </div>
        <div>
            <span class="summary-label">Rider tip</span>
            <strong>${formatMoney(state.confirmedTipAmount ?? 0)}</strong>
        </div>
    `;
}

function renderMap() {
    if (!hasElement("global-status-pill")) {
        return;
    }

    const hasTrip = Boolean(state.request || state.trip);
    placePin("pickup-pin", state.pickupPosition, hasTrip);
    placePin("dropoff-pin", state.dropoffPosition, hasTrip);
    placePin("rider-pin", state.riderPosition, hasTrip && (!state.trip || state.trip.stage !== "completed"));
    placePin("driver-pin", state.driverPosition, hasTrip && (!state.trip || state.trip.stage !== "completed"));
    drawRouteLine();

    if (!hasTrip) {
        setChip("global-status-pill", "No active trip", "neutral");
        $("distance-to-rider").textContent = "-";
        $("trip-stage").textContent = "Waiting for request";
        $("trip-eta").textContent = "-";
        $("map-fare").textContent = "-";
        return;
    }

    const distanceToPickup = distanceKm(state.driverPosition, state.pickupPosition);
    const distanceToDropoff = distanceKm(state.driverPosition, state.dropoffPosition);
    const eta = state.trip && state.trip.stage === "on_trip"
        ? `${Math.max(1, Math.round(Number(distanceToDropoff) * 2))} min`
        : `${Math.max(1, Math.round(Number(distanceToPickup) * 2))} min`;
    const stageText = state.trip ? state.trip.stageLabel : "Awaiting driver decision";

    setChip("global-status-pill", stageText, state.trip ? "info" : "warning");
    $("distance-to-rider").textContent = `${distanceToPickup} km`;
    $("trip-stage").textContent = stageText;
    $("trip-eta").textContent = eta;
    $("map-fare").textContent = state.estimate ? formatMoney(state.estimate.estimated_fare) : "-";
}

function renderAll() {
    applyLanguage();
    renderEstimate();
    renderRider();
    renderDriverRequest();
    renderDriverTrip();
    renderDriverEarnings();
    renderDriverReply();
    renderChat();
    renderMap();
}

async function requestEstimate() {
    if (!bookingForm) {
        return;
    }
    const payload = bookingPayload();

    try {
        const response = await fetch("/api/v1/trips/estimate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                city: "Douala",
                ride_type: payload.ride_type,
                pickup_address: payload.pickup_address,
                destination_address: payload.destination_address,
                distance_km: Number(payload.distance_km),
                duration_minutes: Number(payload.duration_minutes),
                surge_multiplier: 1.0
            })
        });
        if (!response.ok) {
            throw new Error("estimate-request-failed");
        }
        state.estimate = normalizeEstimate(await response.json());
    } catch {
        state.estimate = normalizeEstimate(calculateLocalEstimate(payload));
    }
    renderEstimate();
    renderMap();
}

async function createRideRequest(event) {
    event.preventDefault();
    if (!bookingForm || !session || session.role !== "rider") {
        return;
    }
    try {
        if (!state.estimate) {
            await requestEstimate();
        }

        const payload = bookingPayload();
        const liveState = await liveRequest("request", {
            rider_id: session.id,
            rider_name: session.full_name,
            pickup_address: payload.pickup_address,
            destination_address: payload.destination_address,
            ride_type: payload.ride_type,
            distance_km: Number(payload.distance_km),
            duration_minutes: Number(payload.duration_minutes),
            payment_method: payload.payment_method,
            notes: payload.notes || null,
            estimated_fare: Number(state.estimate.estimated_fare)
        });
        applyLiveState(liveState);
        if (customTipInput) customTipInput.value = "";
        if (driverReplyInput) driverReplyInput.value = "";
        tipButtons.forEach((button) => button.classList.remove("active"));
        setText("rider-request-state", "Ride requested");
        setText("rider-request-copy", "Your request was sent to online drivers.");
        renderAll();
    } catch {
        setChip("rider-status-pill", "Request failed", "danger");
        setText("rider-request-state", "Unable to send request");
        setText("rider-request-copy", "Reload the page and try again.");
    }
}

async function acceptRide() {
    if (!session || session.role !== "driver" || !state.request || state.trip) {
        return;
    }
    try {
        const liveState = await liveRequest("accept", {
            driver_user_id: session.id,
            driver_name: session.full_name,
            vehicle_summary: currentDriverVehicle()
        });
        applyLiveState(liveState);
        renderAll();
    } catch {
        setText("driver-request-box", "Could not accept this request. Reload and try again.");
    }
}

async function declineRide() {
    if (!session || session.role !== "driver" || !state.request || state.trip) {
        return;
    }
    const liveState = await liveRequest("decline", {
        driver_user_id: session.id
    });
    applyLiveState(liveState);
    renderAll();
}

async function markArrived() {
    if (!session || !isAssignedDriver() || !state.trip || state.trip.stage !== "accepted" || !state.arrivalReady) {
        return;
    }
    const liveState = await liveRequest("arrived", {
        driver_user_id: session.id
    });
    applyLiveState(liveState);
    renderAll();
}

async function startTrip() {
    if (!session || !isAssignedDriver() || !state.trip || state.trip.stage !== "driver_arrived") {
        return;
    }
    const liveState = await liveRequest("start", {
        driver_user_id: session.id
    });
    applyLiveState(liveState);
    renderAll();
}

async function completeTrip() {
    if (!session || !isAssignedDriver() || !state.trip || state.trip.stage !== "on_trip") {
        return;
    }
    const liveState = await liveRequest("complete", {
        driver_user_id: session.id
    });
    applyLiveState(liveState);
    renderAll();
}

function selectTip(amount) {
    state.selectedTipAmount = amount;
    tipButtons.forEach((button) => {
        button.classList.toggle("active", Number(button.dataset.tip) === amount);
    });
    renderAll();
}

function applyCustomTip() {
    if (!customTipInput) {
        return;
    }
    const amount = Number(customTipInput.value);
    if (Number.isNaN(amount) || amount < 0) {
        return;
    }
    state.selectedTipAmount = amount;
    tipButtons.forEach((button) => button.classList.remove("active"));
    renderAll();
}

async function confirmTip() {
    if (!state.trip || state.trip.stage !== "completed" || state.selectedTipAmount === null) {
        return;
    }
    const liveState = await liveRequest("tip", {
        amount: Number(state.selectedTipAmount)
    });
    applyLiveState(liveState);
    renderAll();
}

function handleReplyDraft() {
    state.driverReplyDraft = driverReplyInput.value.trim();
    renderAll();
}

function useQuickReply(message) {
    if (!driverReplyInput) {
        return;
    }
    driverReplyInput.value = message;
    state.driverReplyDraft = message;
    renderAll();
}

async function sendDriverReply() {
    const reply = driverReplyInput ? driverReplyInput.value.trim() : "";
    if (!session || !reply || !isAssignedDriver() || state.confirmedTipAmount === null) {
        return;
    }
    const liveState = await liveRequest("reply", {
        driver_user_id: session.id,
        message: reply
    });
    applyLiveState(liveState);
    renderAll();
}

async function sendMessage(inputElement) {
    const message = inputElement ? inputElement.value.trim() : "";
    if (!session || !message || !messagingEnabled()) {
        return;
    }
    const liveState = await liveRequest("message", {
        sender_id: session.id,
        sender_role: session.role,
        sender_name: session.full_name,
        message
    });
    inputElement.value = "";
    applyLiveState(liveState);
    renderAll();
}

async function toggleDriverAvailability() {
    if (!session || session.role !== "driver") {
        return;
    }
    const nextStatus = state.driverAvailability === "online" ? "paused" : "online";
    const liveState = await liveRequest("driver-status", {
        driver_user_id: session.id,
        status: nextStatus
    });
    applyLiveState(liveState);
    renderAll();
}

async function loadAdminMetrics() {
    if (!hasElement("active-trips")) {
        return;
    }
    const [dashboardResponse, pricingResponse, liveStateResponse] = await Promise.all([
        fetch("/api/v1/admin/dashboard"),
        fetch("/api/v1/admin/pricing"),
        fetch("/api/v1/live/state")
    ]);
    const dashboard = await dashboardResponse.json();
    const pricing = await pricingResponse.json();
    const liveState = await liveStateResponse.json();

    $("active-trips").textContent = liveState.trip ? 1 : dashboard.active_trips;
    $("online-drivers").textContent = Object.values(liveState.driver_statuses || {}).filter((status) => status === "online").length;
    $("active-riders").textContent = liveState.request || liveState.trip ? 1 : dashboard.active_riders;
    $("daily-revenue").textContent = formatMoney(dashboard.daily_revenue);
    $("pricing-table").innerHTML = pricing.map((row) => `
        <div class="pricing-row">
            <strong>${row.ride_type}</strong>
            <span>Base ${formatMoney(row.base_fare)}</span>
            <span>Per km ${formatMoney(row.per_km_rate)}</span>
            <span>Per min ${formatMoney(row.per_minute_rate)}</span>
        </div>
    `).join("");
}

async function bootstrapDashboard() {
    if (!session) {
        return;
    }
    hydrateDashboardIdentity();
    if (session.role === "driver") {
        await liveRequest("driver-status", {
            driver_user_id: session.id,
            status: "online"
        });
    }
    await fetchLiveState();
    await loadAdminMetrics();
    if (!state.pollingId) {
        state.pollingId = window.setInterval(async () => {
            try {
                await fetchLiveState();
            } catch {
                return;
            }
        }, 800);
    }
}

if (estimateButton) estimateButton.addEventListener("click", requestEstimate);
if (bookingForm) bookingForm.addEventListener("submit", createRideRequest);
if (refreshPricingButton) refreshPricingButton.addEventListener("click", loadAdminMetrics);
if (toggleDriverStatusButton) toggleDriverStatusButton.addEventListener("click", toggleDriverAvailability);
if (acceptRideButton) acceptRideButton.addEventListener("click", acceptRide);
if (declineRideButton) declineRideButton.addEventListener("click", declineRide);
if (arrivedTripButton) arrivedTripButton.addEventListener("click", markArrived);
if (startTripButton) startTripButton.addEventListener("click", startTrip);
if (completeTripButton) completeTripButton.addEventListener("click", completeTrip);
tipButtons.forEach((button) => {
    button.addEventListener("click", () => selectTip(Number(button.dataset.tip)));
});
if (applyCustomTipButton) applyCustomTipButton.addEventListener("click", applyCustomTip);
if (confirmTipButton) confirmTipButton.addEventListener("click", confirmTip);
if (driverReplyInput) driverReplyInput.addEventListener("input", handleReplyDraft);
replyButtons.forEach((button) => {
    button.addEventListener("click", () => useQuickReply(button.dataset.reply));
});
if (sendDriverReplyButton) sendDriverReplyButton.addEventListener("click", sendDriverReply);
if (sendRiderMessageButton) sendRiderMessageButton.addEventListener("click", () => sendMessage(riderChatInput));
if (sendDriverMessageButton) sendDriverMessageButton.addEventListener("click", () => sendMessage(driverChatInput));
if (riderChatInput) riderChatInput.addEventListener("input", renderChat);
if (driverChatInput) driverChatInput.addEventListener("input", renderChat);
if (languageToggle) {
    languageToggle.value = state.language;
    languageToggle.addEventListener("change", (event) => {
        state.language = event.target.value;
        localStorage.setItem("weis_language", state.language);
        renderAll();
    });
}
if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        if (window.WEISAuth) {
            window.WEISAuth.logout();
        } else {
            sessionStorage.removeItem("weis_session");
            window.location.href = "/";
        }
    });
}

bootstrapDashboard().catch(() => {
    renderAll();
});
