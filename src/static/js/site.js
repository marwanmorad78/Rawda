document.documentElement.classList.add("js-enabled");

const animatedItems = document.querySelectorAll("[data-animate]");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const offerModal = document.querySelector("[data-offer-modal]");
const offerModalImage = offerModal?.querySelector("[data-offer-modal-image]");
const offerModalPlaceholder = offerModal?.querySelector("[data-offer-modal-placeholder]");
const offerModalTitle = offerModal?.querySelector("[data-offer-modal-title]");
const offerModalDescription = offerModal?.querySelector("[data-offer-modal-description]");
const offerModalPrice = offerModal?.querySelector("[data-offer-modal-price]");
const offerModalForm = offerModal?.querySelector("[data-offer-modal-form]");
const productModal = document.querySelector("[data-product-modal]");
const productModalImage = productModal?.querySelector("[data-product-modal-image]");
const productModalPlaceholder = productModal?.querySelector("[data-product-modal-placeholder]");
const productModalTitle = productModal?.querySelector("[data-product-modal-title]");
const productModalDescription = productModal?.querySelector("[data-product-modal-description]");
const productModalCategory = productModal?.querySelector("[data-product-modal-category]");
const productModalPrice = productModal?.querySelector("[data-product-modal-price]");
const productModalForm = productModal?.querySelector("[data-product-modal-form]");
const productModalOptions = productModal?.querySelector("[data-product-modal-options]");
const productModalSubmit = productModal?.querySelector("[data-product-modal-submit]");

const floatingCart = document.querySelector("[data-floating-cart]");
const floatingCartCount = floatingCart?.querySelector("[data-floating-cart-count]");
const floatingCartTotal = floatingCart?.querySelector("[data-floating-cart-total]");
const floatingCartCargo = floatingCart?.querySelector("[data-floating-cart-cargo]");
const cartForms = Array.from(document.querySelectorAll("[data-cart-form]"));
const storeHero = document.querySelector("[data-store-hero]");
const heroCartScene = document.querySelector("[data-hero-cart-scene]");
const heroSceneOverlay = document.querySelector("[data-hero-scene-overlay]");
const heroCategoryChips = Array.from(document.querySelectorAll(".hero-category-chip"));
const heroScrollIndicator = document.querySelector(".hero-scroll-indicator");
const immersiveCartUI = document.querySelector("[data-immersive-cart-ui]");
const immersiveCartHint = immersiveCartUI?.querySelector("[data-immersive-cart-hint]");
const homeTabBar = document.querySelector("[data-home-tab-bar]");
const homeTabs = Array.from(document.querySelectorAll("[data-home-tab]"));
const homeCategoryCards = Array.from(document.querySelectorAll("[data-home-category-card]"));
const productCards = Array.from(document.querySelectorAll("[data-product-card]"));
const productOptionInputs = Array.from(document.querySelectorAll("[data-product-options] input[name='option_id']"));
const productDetailPrice = document.querySelector("[data-product-detail-price]");
const productOptionsSubmit = document.querySelector("[data-product-options-submit]");
const quantityControls = Array.from(document.querySelectorAll("[data-quantity-control]"));
const registerForm = document.querySelector("[data-register-form]");
const syrianPhoneInputs = Array.from(document.querySelectorAll("[data-syrian-phone-input]"));
const syrianPhoneControls = Array.from(document.querySelectorAll("[data-syrian-phone-control]"));
const deliveryAreaGroups = Array.from(document.querySelectorAll("[data-delivery-area-group]"));
const dashboardSubAreaFormsets = Array.from(document.querySelectorAll("[data-dashboard-sub-area-formset]"));
const dashboardDeliveryAreaForms = Array.from(document.querySelectorAll("[data-dashboard-delivery-area-form]"));
const dashboardDrawer = document.querySelector("[data-dashboard-drawer]");
const dashboardDrawerToggle = document.querySelector("[data-dashboard-drawer-toggle]");
const dashboardDrawerClosers = Array.from(document.querySelectorAll("[data-dashboard-drawer-close]"));
const dashboardProductOptionsPanel = document.querySelector("[data-dashboard-product-options-panel]");
const dashboardHasOptionsInput = document.querySelector('input[name="has_options"]');
const dashboardProductBasePriceField = document.querySelector("[data-dashboard-product-base-price-field]");
const dashboardProductBasePriceInput = dashboardProductBasePriceField?.querySelector("input, select, textarea");
const excelModal = document.querySelector("[data-excel-modal]");
const excelModalOpen = document.querySelector("[data-excel-modal-open]");
const excelModalClosers = Array.from(document.querySelectorAll("[data-excel-modal-close]"));
const checkoutAddressModal = document.querySelector("[data-checkout-address-modal]");
const checkoutAddressModalOpen = document.querySelector("[data-checkout-address-modal-open]");
const checkoutAddressModalClosers = Array.from(document.querySelectorAll("[data-checkout-address-modal-close]"));

const cartState = {
    count: Number.parseInt(floatingCart?.dataset.cartCount || "0", 10) || 0,
    total: floatingCart?.dataset.cartTotal || "0",
};
const COMMON_PASSWORDS = new Set([
    "password",
    "password123",
    "12345678",
    "123456789",
    "1234567890",
    "11111111",
    "00000000",
    "qwerty123",
]);
const ARABIC_NAME_PATTERN = /^[\u0621-\u064A\u064B-\u065F]+(?:\s+[\u0621-\u064A\u064B-\u065F]+)*$/;

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
const tabTargetCache = new WeakMap();

const registerMessages = {
    en: {
        required: (label) => `${label} is required.`,
        passwordShort: "Password must contain at least 8 characters.",
        passwordCommon: "This password is too common.",
        passwordNumeric: "Password cannot be entirely numeric.",
        passwordMismatch: "Passwords do not match.",
        phoneInvalid: "يرجى التأكد من ادخال رقم صحيح",
        phoneTaken: "This phone number is already registered.",
        nameArabicOnly: "Please enter the full name in Arabic only.",
        fixBeforeSubmit: "Please fix the highlighted information.",
    },
    ar: {
        required: (label) => `${label} مطلوب.`,
        passwordShort: "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل.",
        passwordCommon: "كلمة المرور شائعة جداً.",
        passwordNumeric: "لا يمكن أن تكون كلمة المرور أرقاماً فقط.",
        passwordMismatch: "كلمتا المرور غير متطابقتين.",
        phoneInvalid: "يرجى التأكد من ادخال رقم صحيح",
        phoneTaken: "رقم الهاتف مسجل مسبقاً.",
        nameArabicOnly: "يرجى إدخال الاسم الكامل باللغة العربية فقط.",
        fixBeforeSubmit: "يرجى تصحيح المعلومات قبل المتابعة.",
    },
};

const getCurrentMessages = () => registerMessages[document.documentElement.lang] || registerMessages.en;
const isArabicLanguage = () => document.documentElement.lang === "ar";
const isArabicNameValue = (value) => ARABIC_NAME_PATTERN.test(String(value || "").trim());

const debounce = (callback, delay = 300) => {
    let timeoutId = null;
    return (...args) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => callback(...args), delay);
    };
};

const setDashboardDrawerOpen = (isOpen) => {
    if (!dashboardDrawer || !dashboardDrawerToggle) {
        return;
    }

    document.body.classList.toggle("is-dashboard-drawer-open", isOpen);
    dashboardDrawerToggle.setAttribute("aria-expanded", String(isOpen));
    dashboardDrawerClosers.forEach((closer) => {
        if (closer.classList.contains("dashboard-drawer-backdrop")) {
            closer.hidden = !isOpen;
        }
    });
};

const syncDashboardProductOptionsPanel = () => {
    if (!dashboardHasOptionsInput) {
        return;
    }
    const hasOptions = dashboardHasOptionsInput.checked;
    if (dashboardProductOptionsPanel) {
        dashboardProductOptionsPanel.hidden = !hasOptions;
    }
    if (dashboardProductBasePriceField) {
        dashboardProductBasePriceField.hidden = hasOptions;
    }
    if (dashboardProductBasePriceInput) {
        dashboardProductBasePriceInput.disabled = hasOptions;
        dashboardProductBasePriceInput.required = !hasOptions;
    }
};

const setExcelModalOpen = (isOpen) => {
    if (!excelModal) {
        return;
    }
    excelModal.hidden = !isOpen;
    document.body.classList.toggle("modal-open", isOpen);
};

const setCheckoutAddressModalOpen = (isOpen) => {
    if (!checkoutAddressModal) {
        return;
    }
    checkoutAddressModal.hidden = !isOpen;
    document.body.classList.toggle("modal-open", isOpen);
};

const getQuantityValue = (input) => {
    const minimum = Number.parseInt(input.min || "1", 10) || 1;
    const current = Number.parseInt(input.value || String(minimum), 10);
    return Math.max(Number.isNaN(current) ? minimum : current, minimum);
};

const setQuantityValue = (input, value) => {
    if (!input) {
        return;
    }

    const minimum = Number.parseInt(input.min || "1", 10) || 1;
    input.value = String(Math.max(value, minimum));
};

const normalizeLabel = (value) =>
    String(value || "")
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^\p{L}\p{N}]+/gu, " ")
        .trim();

const normalizeSyrianPhoneValue = (value) => {
    let digits = String(value || "").replace(/\D+/g, "");

    if (digits.startsWith("00")) {
        digits = digits.slice(2);
    }

    if (digits.startsWith("963")) {
        digits = digits.slice(3);
    }

    if (digits.length >= 2 && digits.startsWith("09")) {
        digits = digits.slice(1);
    }

    return digits.slice(0, 9);
};

const isValidSyrianPhoneValue = (value) => /^9\d{8}$/.test(normalizeSyrianPhoneValue(value));

const syncSyrianPhoneInput = (input) => {
    if (!input) {
        return "";
    }

    const normalizedPhone = normalizeSyrianPhoneValue(input.value);
    if (input.value !== normalizedPhone) {
        input.value = normalizedPhone;
    }
    return normalizedPhone;
};

const enhanceSyrianPhoneInput = (input) => {
    if (!input) {
        return;
    }

    const applyNormalization = () => syncSyrianPhoneInput(input);

    applyNormalization();
    input.addEventListener("input", applyNormalization);
    input.addEventListener("blur", applyNormalization);
    input.form?.addEventListener("submit", applyNormalization);
};

const closeSyrianPhoneMenu = (control) => {
    if (!control) {
        return;
    }

    const toggle = control.querySelector("[data-syrian-phone-toggle]");
    const menu = control.querySelector("[data-syrian-phone-menu]");
    control.classList.remove("is-open");
    toggle?.setAttribute("aria-expanded", "false");
    if (menu) {
        menu.hidden = true;
    }
};

const openSyrianPhoneMenu = (control) => {
    if (!control) {
        return;
    }

    syrianPhoneControls.forEach((item) => {
        if (item !== control) {
            closeSyrianPhoneMenu(item);
        }
    });

    const toggle = control.querySelector("[data-syrian-phone-toggle]");
    const menu = control.querySelector("[data-syrian-phone-menu]");
    control.classList.add("is-open");
    toggle?.setAttribute("aria-expanded", "true");
    if (menu) {
        menu.hidden = false;
    }
};

const enhanceSyrianPhoneControl = (control) => {
    if (!control) {
        return;
    }

    const toggle = control.querySelector("[data-syrian-phone-toggle]");
    const option = control.querySelector("[data-syrian-phone-option]");
    const input = control.querySelector("[data-syrian-phone-input]");

    toggle?.addEventListener("click", (event) => {
        event.preventDefault();
        const isOpen = control.classList.contains("is-open");
        if (isOpen) {
            closeSyrianPhoneMenu(control);
            input?.focus();
            return;
        }
        openSyrianPhoneMenu(control);
    });

    option?.addEventListener("click", () => {
        closeSyrianPhoneMenu(control);
        input?.focus();
    });
};

const enhanceDeliveryAreaGroup = (group) => {
    if (!group) {
        return;
    }

    const areaSelect = group.querySelector("[data-delivery-area-select]");
    const subAreaWrapper = group.querySelector("[data-sub-area-wrapper]");
    const subAreaSelect = group.querySelector("[data-delivery-sub-area-select]");
    const urlTemplate = group.dataset.subareasUrlTemplate || "";
    const placeholder = subAreaSelect?.dataset.placeholder || "";

    if (!areaSelect || !subAreaWrapper || !subAreaSelect || !urlTemplate) {
        return;
    }

    const setSubAreaOptions = (items, selectedValue = "") => {
        subAreaSelect.replaceChildren();

        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = placeholder;
        subAreaSelect.append(placeholderOption);

        items.forEach((item) => {
            const option = document.createElement("option");
            option.value = String(item.id);
            option.textContent = item.name;
            if (String(item.id) === String(selectedValue)) {
                option.selected = true;
            }
            subAreaSelect.append(option);
        });
    };

    const hideSubAreaField = () => {
        setSubAreaOptions([]);
        subAreaSelect.value = "";
        subAreaWrapper.hidden = true;
    };

    const syncSubAreas = async ({ preserveSelection = true } = {}) => {
        const areaId = areaSelect.value;
        if (!areaId) {
            hideSubAreaField();
            return;
        }

        try {
            const response = await window.fetch(urlTemplate.replace("/0/", `/${areaId}/`), {
                headers: { Accept: "application/json" },
            });
            if (!response.ok) {
                hideSubAreaField();
                return;
            }

            const payload = await response.json();
            const items = Array.isArray(payload.sub_areas) ? payload.sub_areas : [];
            if (!items.length) {
                hideSubAreaField();
                return;
            }

            const selectedValue = preserveSelection ? subAreaSelect.value : "";
            setSubAreaOptions(items, selectedValue);
            subAreaWrapper.hidden = false;
        } catch (error) {
            hideSubAreaField();
        }
    };

    areaSelect.addEventListener("change", () => {
        subAreaSelect.value = "";
        syncSubAreas({ preserveSelection: false });
    });

    syncSubAreas();
};

const enhanceDashboardSubAreaFormset = (formset) => {
    if (!formset) {
        return;
    }

    const rowsContainer = formset.querySelector("[data-sub-area-rows]");
    const addButton = formset.querySelector("[data-add-sub-area]");
    const emptyTemplate = formset.querySelector("[data-sub-area-empty-form]");
    const totalFormsInput = formset.querySelector('input[name$="-TOTAL_FORMS"]');

    if (!rowsContainer || !addButton || !emptyTemplate || !totalFormsInput) {
        return;
    }

    addButton.addEventListener("click", () => {
        const nextIndex = Number.parseInt(totalFormsInput.value || "0", 10) || 0;
        const templateMarkup = emptyTemplate.innerHTML.replace(/__prefix__/g, String(nextIndex)).trim();

        if (!templateMarkup) {
            return;
        }

        rowsContainer.insertAdjacentHTML("beforeend", templateMarkup);
        totalFormsInput.value = String(nextIndex + 1);
    });
};

const enhanceDashboardDeliveryAreaForm = (form) => {
    if (!form) {
        return;
    }

    const hasSubAreasInput = form.querySelector('[name="has_sub_areas"]');
    const mainFeeField = form.querySelector("[data-main-delivery-fee-field]");
    const subAreaPanel = form.querySelector("[data-dashboard-sub-area-formset]");

    if (!hasSubAreasInput || !mainFeeField || !subAreaPanel) {
        return;
    }

    const syncAreaPricingMode = () => {
        const usesSubAreaPricing = Boolean(hasSubAreasInput.checked);
        mainFeeField.hidden = usesSubAreaPricing;
        subAreaPanel.hidden = !usesSubAreaPricing;
    };

    hasSubAreasInput.addEventListener("change", syncAreaPricingMode);
    syncAreaPricingMode();
};

const getFallbackTarget = (tab) => {
    const fallbackId = tab?.dataset.fallbackId;
    return fallbackId ? document.getElementById(fallbackId) : null;
};

const resolveHomeTabTarget = (tab) => {
    if (!tab) {
        return null;
    }

    if (tabTargetCache.has(tab)) {
        return tabTargetCache.get(tab);
    }

    let target = getFallbackTarget(tab);
    const matchTokens = String(tab.dataset.categoryMatch || "")
        .split("|")
        .map(normalizeLabel)
        .filter(Boolean);

    if (matchTokens.length) {
        target =
            homeCategoryCards.find((card) => {
                const name = normalizeLabel(card.dataset.categoryName);
                const slug = normalizeLabel(card.dataset.categorySlug);
                return matchTokens.some((token) => name.includes(token) || slug.includes(token));
            }) || target;
    }

    tabTargetCache.set(tab, target);
    return target;
};

const setActiveHomeTab = (activeKey) => {
    homeTabs.forEach((tab) => {
        tab.classList.toggle("is-active", tab.dataset.tabKey === activeKey);
    });
};

const syncActiveHomeTab = () => {
    if (!homeTabs.length) {
        return;
    }

    const anchorY = window.scrollY + window.innerHeight * 0.34;
    let activeTab = homeTabs[0];
    let bestDistance = Number.POSITIVE_INFINITY;

    homeTabs.forEach((tab) => {
        const target = resolveHomeTabTarget(tab);
        if (!target) {
            return;
        }

        const targetY = window.scrollY + target.getBoundingClientRect().top;
        const distance = Math.abs(targetY - anchorY);

        if (distance < bestDistance) {
            bestDistance = distance;
            activeTab = tab;
        }
    });

    setActiveHomeTab(activeTab?.dataset.tabKey || "home");
};

const renderCargo = (container, count) => {
    if (!container) {
        return;
    }

    container.replaceChildren();
    const visibleCount = clamp(count, 0, 4);

    for (let index = 0; index < visibleCount; index += 1) {
        const chip = document.createElement("span");
        chip.className = "cart-cargo-chip";
        container.append(chip);
    }
};

const syncCartState = () => {
    if (!floatingCart) {
        if (immersiveCartHint) {
            const cartLabel = immersiveCartHint.dataset.cartLabel || "Cart";
            immersiveCartHint.textContent = cartState.count > 0 ? `${cartLabel} ${cartState.count}` : cartLabel;
        }
        return;
    }

    floatingCart.dataset.cartCount = String(cartState.count);
    floatingCart.dataset.cartTotal = cartState.total;
    floatingCart.classList.toggle("is-empty", cartState.count <= 0);

    if (floatingCartCount) {
        floatingCartCount.textContent = String(cartState.count);
    }

    if (floatingCartTotal) {
        floatingCartTotal.textContent = cartState.total;
    }

    renderCargo(floatingCartCargo, cartState.count);

    if (immersiveCartHint) {
        const cartLabel = immersiveCartHint.dataset.cartLabel || "Cart";
        immersiveCartHint.textContent = cartState.count > 0 ? `${cartLabel} ${cartState.count}` : cartLabel;
    }
};

const bumpCart = () => {
    if (!floatingCart) {
        if (immersiveCartUI) {
            immersiveCartUI.classList.remove("is-bumping");
            void immersiveCartUI.offsetWidth;
            immersiveCartUI.classList.add("is-bumping");
        }
        return;
    }

    floatingCart.classList.remove("is-bumping");
    void floatingCart.offsetWidth;
    floatingCart.classList.add("is-bumping");

    if (immersiveCartUI) {
        immersiveCartUI.classList.remove("is-bumping");
        void immersiveCartUI.offsetWidth;
        immersiveCartUI.classList.add("is-bumping");
    }
};

const showToast = (message) => {
    if (!message) {
        return;
    }

    document.querySelector(".cart-toast")?.remove();

    const toast = document.createElement("div");
    toast.className = "cart-toast";
    toast.textContent = message;
    document.body.append(toast);

    window.setTimeout(() => {
        toast.remove();
    }, 2800);
};

const showCartToast = showToast;

const showToastMessages = (messages) => {
    const uniqueMessages = [...new Set(messages.filter(Boolean))];
    showToast(uniqueMessages.join("\n"));
};

const showFieldToast = (field, message) => {
    if (!message) {
        return;
    }

    document.querySelectorAll(".field-toast").forEach((toast) => toast.remove());

    if (!field) {
        showToast(message);
        return;
    }

    const container = field.closest("label") || field.parentElement;
    if (!container) {
        showToast(message);
        return;
    }

    container.classList.add("has-field-toast");
    const toast = document.createElement("span");
    toast.className = "field-toast is-error";
    toast.textContent = message;
    container.append(toast);

    window.setTimeout(() => {
        toast.remove();
    }, 2600);
};

const getFieldValidationTarget = (field) => field?.closest("[data-syrian-phone-control]") || field;

const setFieldValidationState = (field, state) => {
    const target = getFieldValidationTarget(field);
    if (!target) {
        return;
    }

    target.classList.remove("validation-valid", "validation-invalid");
    if (state === "valid") {
        target.classList.add("validation-valid");
    } else if (state === "invalid") {
        target.classList.add("validation-invalid");
    }

    if (state === "valid") {
        target.style.borderColor = "#1b8f3a";
        target.style.boxShadow = "0 0 0 4px rgba(27, 143, 58, 0.2)";
    } else if (state === "invalid") {
        target.style.borderColor = "#c62828";
        target.style.boxShadow = "0 0 0 4px rgba(198, 40, 40, 0.22)";
    } else {
        target.style.borderColor = "";
        target.style.boxShadow = "";
    }
};

const getPasswordValidationState = () => {
    if (!registerForm) {
        return null;
    }

    const passwordInput = registerForm.querySelector('[name="password1"]');
    const confirmPasswordInput = registerForm.querySelector('[name="password2"]');
    const password = passwordInput?.value || "";
    const confirmPassword = confirmPasswordInput?.value || "";

    const passwordValid = Boolean(
        password &&
        password.length >= 8 &&
        !COMMON_PASSWORDS.has(password.toLowerCase()) &&
        !/^\d+$/.test(password),
    );

    const confirmValid = Boolean(confirmPassword && passwordValid && password === confirmPassword);

    return {
        passwordInput,
        confirmPasswordInput,
        passwordValue: password,
        confirmValue: confirmPassword,
        passwordValid,
        confirmValid,
    };
};

const applyStoreHeroProgress = (progress) => {
    if (!storeHero || !heroCartScene) {
        return;
    }

    const heroHeight = Math.max(storeHero.offsetHeight, 1);
    const overlayOpacity = 0.08 + progress * 0.18;
    const sceneScale = 1 + progress * 0.03;
    const cartTravelY = -Math.min(heroHeight * 0.12, 96) * progress;
    const cartScale = 1 - progress * 0.04;
    const cartRotate = progress * -0.25;
    const cartOpacity = 1;
    const shadowScale = 1 - progress * 0.04;
    const orbitProgress = clamp((progress - 0.08) / 0.18, 0, 1);

    storeHero.style.setProperty("--hero-overlay-opacity", overlayOpacity.toFixed(3));
    storeHero.style.setProperty("--hero-scene-scale", sceneScale.toFixed(3));
    storeHero.style.setProperty("--hero-cart-x", "0px");
    storeHero.style.setProperty("--hero-cart-y", `${cartTravelY.toFixed(1)}px`);
    storeHero.style.setProperty("--hero-cart-scale", cartScale.toFixed(3));
    storeHero.style.setProperty("--hero-cart-rotate", `${cartRotate.toFixed(1)}deg`);
    storeHero.style.setProperty("--hero-cart-opacity", cartOpacity.toFixed(3));
    storeHero.style.setProperty("--hero-cart-shadow-scale", shadowScale.toFixed(3));
    immersiveCartUI?.style.setProperty("--immersive-cart-y", `${cartTravelY.toFixed(1)}px`);
    immersiveCartUI?.style.setProperty("--immersive-cart-scale", cartScale.toFixed(3));
    immersiveCartUI?.style.setProperty("--immersive-orbit-opacity", orbitProgress.toFixed(3));
    immersiveCartUI?.style.setProperty("--immersive-orbit-y", `${((1 - orbitProgress) * 24).toFixed(1)}px`);
    immersiveCartUI?.style.setProperty("--immersive-orbit-scale", (0.92 + orbitProgress * 0.08).toFixed(3));
    document.body.classList.toggle("is-home-nav-revealed", orbitProgress > 0.04);

    if (heroSceneOverlay) {
        heroSceneOverlay.style.opacity = overlayOpacity.toFixed(3);
    }

    heroCategoryChips.forEach((chip, index) => {
        const threshold = 0.06 + index * 0.03;
        const localProgress = clamp((progress - threshold) / 0.18, 0, 1);
        const offsetY = (1 - localProgress) * (22 + index * 3);
        const direction = index % 2 === 0 ? -1 : 1;
        const offsetX = (1 - localProgress) * direction * 18;
        const scale = 0.9 + localProgress * 0.1;

        chip.style.opacity = localProgress.toFixed(3);
        chip.style.transform = `translate3d(${offsetX.toFixed(1)}px, ${offsetY.toFixed(1)}px, 0) scale(${scale.toFixed(3)})`;
    });

    if (heroScrollIndicator) {
        heroScrollIndicator.style.opacity = String(clamp(1 - progress * 2.2, 0, 1));
        heroScrollIndicator.style.transform = `translateX(-50%) translateY(${(progress * 12).toFixed(1)}px)`;
    }

    if (homeTabBar) {
        syncActiveHomeTab();
    }
};

const animateStoreHeroOnScroll = () => {
    if (!storeHero || !heroCartScene) {
        return;
    }

    const start = storeHero.offsetTop;
    const end = start + Math.max(storeHero.offsetHeight - window.innerHeight, 1);
    const progress = clamp((window.scrollY - start) / Math.max(end - start, 1), 0, 1);
    applyStoreHeroProgress(progress);
};

const openOfferModal = (slide) => {
    if (!offerModal || !offerModalTitle || !offerModalDescription || !offerModalPrice || !offerModalForm) {
        return;
    }

    const title = slide.dataset.offerTitle || "";
    const description = slide.dataset.offerDescription || "";
    const price = slide.dataset.offerPrice || "";
    const image = slide.dataset.offerImage || "";
    const action = slide.dataset.offerAction || "";

    offerModalTitle.textContent = title;
    offerModalDescription.textContent = description;
    offerModalPrice.textContent = price;
    offerModalForm.action = action;
    offerModalForm.dataset.cartItemTitle = title;
    offerModalForm.dataset.cartItemImage = image;

    if (offerModalImage && offerModalPlaceholder) {
        if (image) {
            offerModalImage.src = image;
            offerModalImage.alt = title;
            offerModalImage.hidden = false;
            offerModalPlaceholder.hidden = true;
        } else {
            offerModalImage.hidden = true;
            offerModalPlaceholder.hidden = false;
            offerModalPlaceholder.textContent = title.slice(0, 1);
        }
    }

    offerModal.hidden = false;
    document.body.classList.add("modal-open");
};

const closeOfferModal = () => {
    if (!offerModal) {
        return;
    }

    offerModal.hidden = true;
    document.body.classList.remove("modal-open");
};

const openProductModal = (card) => {
    if (!productModal || !productModalTitle || !productModalPrice || !productModalForm) {
        return;
    }

    const title = card.dataset.productTitle || "";
    const description = card.dataset.productDescription || "";
    const category = card.dataset.productCategory || "";
    const price = card.dataset.productPrice || "";
    const image = card.dataset.productImage || "";
    const action = card.dataset.productAction || "";

    productModalTitle.textContent = title;
    productModalPrice.textContent = price;
    productModalForm.action = action;
    productModalForm.dataset.cartItemTitle = title;
    productModalForm.dataset.cartItemImage = image;
    setQuantityValue(productModalForm.querySelector('input[name="quantity"]'), 1);

    if (productModalOptions && productModalSubmit) {
        const optionNodes = Array.from(card.querySelectorAll("[data-product-options-source] [data-option-id]"));
        productModalOptions.querySelectorAll(".product-option-card").forEach((option) => option.remove());
        productModalOptions.hidden = optionNodes.length === 0;
        productModalSubmit.disabled = optionNodes.length > 0;

        optionNodes.forEach((optionNode) => {
            const label = document.createElement("label");
            label.className = "product-option-card";

            const input = document.createElement("input");
            input.type = "radio";
            input.name = "option_id";
            input.value = optionNode.dataset.optionId || "";
            input.required = true;
            input.dataset.optionPrice = optionNode.dataset.optionPrice || "";
            input.checked = optionNode.dataset.optionDefault === "true";

            const mark = document.createElement("span");
            mark.className = "choice-mark choice-mark-radio";
            mark.setAttribute("aria-hidden", "true");

            const copy = document.createElement("span");
            copy.className = "choice-copy";
            const name = document.createElement("strong");
            name.textContent = optionNode.dataset.optionName || "";
            const optionPrice = document.createElement("small");
            optionPrice.textContent = optionNode.dataset.optionPrice || "";
            copy.append(name, optionPrice);

            input.addEventListener("change", () => {
                productModalPrice.textContent = input.dataset.optionPrice || price;
                productModalSubmit.disabled = false;
            });

            label.append(input, mark, copy);
            productModalOptions.append(label);

            if (input.checked) {
                productModalPrice.textContent = input.dataset.optionPrice || price;
                productModalSubmit.disabled = false;
            }
        });
    }

    if (productModalDescription) {
        productModalDescription.textContent = description;
        productModalDescription.hidden = !description;
    }

    if (productModalCategory) {
        productModalCategory.textContent = category;
        productModalCategory.hidden = !category;
    }

    if (productModalImage && productModalPlaceholder) {
        if (image) {
            productModalImage.src = image;
            productModalImage.alt = title;
            productModalImage.hidden = false;
            productModalPlaceholder.hidden = true;
        } else {
            productModalImage.hidden = true;
            productModalPlaceholder.hidden = false;
            productModalPlaceholder.textContent = title.slice(0, 1);
        }
    }

    productModal.hidden = false;
    document.body.classList.add("modal-open");
};

const closeProductModal = () => {
    if (!productModal) {
        return;
    }

    productModal.hidden = true;
    document.body.classList.remove("modal-open");
};

const closeModals = () => {
    closeOfferModal();
    closeProductModal();
    setExcelModalOpen(false);
    setCheckoutAddressModalOpen(false);
};

const enhanceCartForm = (form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const formData = new FormData(form);

        try {
            if (submitButton) {
                submitButton.disabled = true;
            }

            const response = await window.fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error(`Cart request failed with status ${response.status}`);
            }

            const payload = await response.json();

            if (!payload.ok) {
                throw new Error("Cart update returned an unexpected payload.");
            }

            cartState.count = Number.parseInt(String(payload.cart_count || cartState.count), 10) || cartState.count;
            cartState.total = payload.cart_total || cartState.total;

            if (floatingCart && payload.cart_url) {
                floatingCart.href = payload.cart_url;
            }

            syncCartState();
            bumpCart();
            showCartToast(payload.message || "");
            closeModals();
        } catch (error) {
            form.submit();
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
};

const getFieldLabel = (field) => {
    const label = field.closest("label");
    return label?.querySelector("span")?.textContent?.trim() || field.name || "Field";
};

const collectRegisterPasswordErrors = () => {
    if (!registerForm) {
        return [];
    }

    const messages = getCurrentMessages();
    const validationState = getPasswordValidationState();
    const passwordInput = validationState?.passwordInput;
    const confirmPasswordInput = validationState?.confirmPasswordInput;
    const password = validationState?.passwordValue || "";
    const confirmPassword = validationState?.confirmValue || "";
    const errors = [];

    if (password && password.length < 8) {
        errors.push({ field: passwordInput, message: messages.passwordShort });
    }

    if (password && COMMON_PASSWORDS.has(password.toLowerCase())) {
        errors.push({ field: passwordInput, message: messages.passwordCommon });
    }

    if (password && /^\d+$/.test(password)) {
        errors.push({ field: passwordInput, message: messages.passwordNumeric });
    }

    if (password && confirmPassword && password !== confirmPassword) {
        errors.push({ field: confirmPasswordInput, message: messages.passwordMismatch });
    }

    return errors;
};

const collectRegisterNameErrors = () => {
    if (!registerForm || !isArabicLanguage()) {
        return [];
    }

    const messages = getCurrentMessages();
    const nameInput = registerForm.querySelector('[name="full_name"]');
    const name = String(nameInput?.value || "").trim();

    if (name && !isArabicNameValue(name)) {
        return [{ field: nameInput, message: messages.nameArabicOnly }];
    }

    return [];
};

const collectRegisterRequiredErrors = () => {
    if (!registerForm) {
        return [];
    }

    const messages = getCurrentMessages();
    return Array.from(registerForm.querySelectorAll("input, select, textarea"))
        .filter((field) => field.required && !String(field.value || "").trim())
        .map((field) => ({ field, message: messages.required(getFieldLabel(field)) }));
};

const collectRegisterClientErrors = () => {
    const errors = [...collectRegisterRequiredErrors(), ...collectRegisterNameErrors(), ...collectRegisterPasswordErrors()];
    const messages = getCurrentMessages();
    const phoneInput = registerForm?.querySelector('[name="username"]');

    if (phoneInput?.value && !isValidSyrianPhoneValue(phoneInput.value)) {
        errors.push({ field: phoneInput, message: messages.phoneInvalid });
    }

    if (phoneInput?.dataset.phoneTaken === "true") {
        errors.push({ field: phoneInput, message: messages.phoneTaken });
    }

    return errors;
};

const showRegisterError = (error) => {
    if (!error) {
        return;
    }

    if (typeof error === "string") {
        showToast(error);
        return;
    }

    setFieldValidationState(error.field, "invalid");
    showFieldToast(error.field, error.message);
};

const showRegisterServerErrors = () => {
    if (!registerForm) {
        return;
    }

    const errors = Array.from(registerForm.querySelectorAll(".errorlist"))
        .flatMap((list) => {
            list.classList.add("toast-hidden-error");
            const field = list.closest("label")?.querySelector("input, select, textarea");
            return Array.from(list.querySelectorAll("li")).map((item) => ({
                field,
                message: item.textContent.trim(),
            }));
        })
        .filter((error) => error.message);

    showRegisterError(errors[0]);
};

const enhanceRegisterForm = () => {
    if (!registerForm) {
        return;
    }

    const messages = getCurrentMessages();
    const nameInput = registerForm.querySelector('[name="full_name"]');
    const phoneInput = registerForm.querySelector('[name="username"]');
    const passwordInputs = Array.from(registerForm.querySelectorAll('[name="password1"], [name="password2"]'));
    let lastLiveNameErrorMessage = "";
    let lastLiveErrorMessage = "";
    let lastLivePhoneErrorMessage = "";

    const updatePasswordValidationStates = () => {
        const validationState = getPasswordValidationState();
        if (!validationState) {
            return;
        }

        const {
            passwordInput,
            confirmPasswordInput,
            passwordValue,
            confirmValue,
            passwordValid,
            confirmValid,
        } = validationState;

        setFieldValidationState(passwordInput, passwordValue ? (passwordValid ? "valid" : "invalid") : null);
        setFieldValidationState(confirmPasswordInput, confirmValue ? (confirmValid ? "valid" : "invalid") : null);
    };

    const updatePhoneValidationState = (state) => {
        setFieldValidationState(phoneInput, state);
    };

    const updateNameValidationState = () => {
        if (!nameInput || !isArabicLanguage()) {
            return;
        }

        const name = String(nameInput.value || "").trim();
        setFieldValidationState(nameInput, name ? (isArabicNameValue(name) ? "valid" : "invalid") : null);
    };

    const showLiveNameError = debounce(() => {
        if (!nameInput || !isArabicLanguage()) {
            return;
        }

        const errors = collectRegisterNameErrors();
        const firstError = errors[0];
        const nextMessage = firstError?.message || "";

        if (nextMessage && nextMessage !== lastLiveNameErrorMessage) {
            showRegisterError(firstError);
        }

        lastLiveNameErrorMessage = nextMessage;
    }, 400);

    const showLivePasswordErrors = debounce(() => {
        const errors = collectRegisterPasswordErrors();
        const firstError = errors[0];
        const nextMessage = firstError?.message || "";

        if (nextMessage && nextMessage !== lastLiveErrorMessage) {
            showRegisterError(firstError);
        }

        lastLiveErrorMessage = nextMessage;
    }, 400);

    const handlePhoneInput = () => {
        if (!phoneInput) {
            return;
        }

        const phone = syncSyrianPhoneInput(phoneInput);
        if (!phone) {
            phoneInput.dataset.phoneTaken = "false";
            lastLivePhoneErrorMessage = "";
            updatePhoneValidationState(null);
            return;
        }

        if (!isValidSyrianPhoneValue(phone)) {
            phoneInput.dataset.phoneTaken = "false";
            updatePhoneValidationState("invalid");
        } else {
            updatePhoneValidationState(null);
        }

        checkPhone();
    };

    const checkPhone = debounce(async () => {
        if (!phoneInput || !registerForm.dataset.phoneCheckUrl) {
            return;
        }

        const phone = syncSyrianPhoneInput(phoneInput);
        if (!phone) {
            phoneInput.dataset.phoneTaken = "false";
            lastLivePhoneErrorMessage = "";
            updatePhoneValidationState(null);
            return;
        }

        if (!isValidSyrianPhoneValue(phone)) {
            phoneInput.dataset.phoneTaken = "false";
            updatePhoneValidationState("invalid");
            if (messages.phoneInvalid !== lastLivePhoneErrorMessage) {
                showFieldToast(phoneInput, messages.phoneInvalid);
            }
            lastLivePhoneErrorMessage = messages.phoneInvalid;
            return;
        }

        try {
            const url = new URL(registerForm.dataset.phoneCheckUrl, window.location.origin);
            url.searchParams.set("phone", phone);
            const response = await window.fetch(url, { headers: { Accept: "application/json" } });
            const payload = await response.json();
            phoneInput.dataset.phoneTaken = payload.exists ? "true" : "false";

            const nextMessage = payload.exists ? messages.phoneTaken : "";
            updatePhoneValidationState(payload.exists ? "invalid" : "valid");
            if (nextMessage && nextMessage !== lastLivePhoneErrorMessage) {
                showFieldToast(phoneInput, messages.phoneTaken);
            }
            lastLivePhoneErrorMessage = nextMessage;
        } catch (error) {
            phoneInput.dataset.phoneTaken = "false";
            lastLivePhoneErrorMessage = "";
            updatePhoneValidationState(null);
        }
    }, 500);

    showRegisterServerErrors();
    updateNameValidationState();
    updatePasswordValidationStates();
    nameInput?.addEventListener("input", () => {
        updateNameValidationState();
        showLiveNameError();
    });
    nameInput?.addEventListener("blur", () => {
        updateNameValidationState();
        const errors = collectRegisterNameErrors();
        if (errors.length) {
            showRegisterError(errors[0]);
            lastLiveNameErrorMessage = errors[0].message;
        }
    });
    passwordInputs.forEach((input) =>
        input.addEventListener("input", () => {
            updatePasswordValidationStates();
            showLivePasswordErrors();
        }),
    );
    phoneInput?.addEventListener("input", handlePhoneInput);
    phoneInput?.addEventListener("blur", () => {
        const phone = syncSyrianPhoneInput(phoneInput);
        if (phone && !isValidSyrianPhoneValue(phone)) {
            updatePhoneValidationState("invalid");
            showFieldToast(phoneInput, messages.phoneInvalid);
            lastLivePhoneErrorMessage = messages.phoneInvalid;
        }
    });

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const clientErrors = collectRegisterClientErrors();
        if (clientErrors.length) {
            showRegisterError(clientErrors[0]);
            return;
        }

        const submitButton = registerForm.querySelector('button[type="submit"]');
        const formData = new FormData(registerForm);
        if (phoneInput) {
            const phone = syncSyrianPhoneInput(phoneInput);
            formData.set(phoneInput.name, phone);
        }

        try {
            if (submitButton) {
                submitButton.disabled = true;
            }

            const response = await window.fetch(registerForm.action || window.location.href, {
                method: "POST",
                body: formData,
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const payload = await response.json();

            if (payload.ok && payload.redirect_url) {
                window.location.href = payload.redirect_url;
                return;
            }

            const fieldErrors = payload.field_errors || {};
            const fieldName = Object.keys(fieldErrors).find((name) => name !== "__all__" && fieldErrors[name]?.length);
            if (fieldName) {
                const field = registerForm.querySelector(`[name="${fieldName}"]`);
                setFieldValidationState(field, "invalid");
                showFieldToast(field, fieldErrors[fieldName][0]);
                return;
            }

            showToast(payload.errors?.[0] || messages.fixBeforeSubmit);
        } catch (error) {
            registerForm.submit();
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
};

syrianPhoneInputs.forEach(enhanceSyrianPhoneInput);
syrianPhoneControls.forEach(enhanceSyrianPhoneControl);
deliveryAreaGroups.forEach(enhanceDeliveryAreaGroup);
dashboardSubAreaFormsets.forEach(enhanceDashboardSubAreaFormset);
dashboardDeliveryAreaForms.forEach(enhanceDashboardDeliveryAreaForm);

document.addEventListener("click", (event) => {
    syrianPhoneControls.forEach((control) => {
        if (!control.contains(event.target)) {
            closeSyrianPhoneMenu(control);
        }
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }

    syrianPhoneControls.forEach(closeSyrianPhoneMenu);
});

if (animatedItems.length) {
    if (prefersReducedMotion.matches || !("IntersectionObserver" in window)) {
        animatedItems.forEach((item) => item.classList.add("is-visible"));
    } else {
        const revealObserver = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                });
            },
            {
                threshold: 0.16,
                rootMargin: "0px 0px -8% 0px",
            },
        );

        animatedItems.forEach((item) => revealObserver.observe(item));
    }
}

const carousels = document.querySelectorAll("[data-carousel]");

carousels.forEach((carousel) => {
    const slides = Array.from(carousel.querySelectorAll("[data-carousel-slide]"));
    const dots = Array.from(carousel.querySelectorAll("[data-carousel-dot]"));
    const prevButton = carousel.querySelector("[data-carousel-prev]");
    const nextButton = carousel.querySelector("[data-carousel-next]");
    const intervalMs = Number(carousel.dataset.carouselInterval || 4500);

    if (!slides.length) {
        return;
    }

    slides.forEach((slide, index) => {
        slide.dataset.carouselIndex = String(index);
    });

    let currentIndex = slides.findIndex((slide) => slide.classList.contains("is-active"));
    if (currentIndex < 0) {
        currentIndex = 0;
    }

    let timerId = null;

    const getWrappedIndex = (index) => {
        const total = slides.length;
        return ((index % total) + total) % total;
    };

    const showSlide = (nextIndex) => {
        const activeIndex = getWrappedIndex(nextIndex);
        const prevIndex = getWrappedIndex(activeIndex - 1);
        const nextVisibleIndex = getWrappedIndex(activeIndex + 1);
        const hasFarSlides = slides.length > 4;
        const farPrevIndex = hasFarSlides ? getWrappedIndex(activeIndex - 2) : -1;
        const farNextIndex = hasFarSlides ? getWrappedIndex(activeIndex + 2) : -1;

        slides.forEach((slide, index) => {
            const stateClass =
                index === activeIndex
                    ? "is-active"
                    : index === prevIndex
                      ? "is-prev"
                      : index === nextVisibleIndex
                        ? "is-next"
                        : index === farPrevIndex
                          ? "is-far-prev"
                          : index === farNextIndex
                            ? "is-far-next"
                            : "";

            slide.classList.remove("is-active", "is-prev", "is-next", "is-far-prev", "is-far-next");
            if (stateClass) {
                slide.classList.add(stateClass);
            }
            slide.setAttribute("aria-hidden", String(!(stateClass === "is-active" || stateClass === "is-prev" || stateClass === "is-next")));
        });

        dots.forEach((dot, index) => {
            const isActive = index === activeIndex;
            dot.classList.toggle("is-active", isActive);
            dot.setAttribute("aria-pressed", String(isActive));
        });

        currentIndex = activeIndex;
    };

    carousel.addEventListener("click", (event) => {
        const slide = event.target.closest("[data-carousel-slide]");
        if (!slide || !carousel.contains(slide)) {
            return;
        }

        const clickedIndex = Number(slide.dataset.carouselIndex);
        if (Number.isNaN(clickedIndex)) {
            return;
        }

        event.preventDefault();
        if (clickedIndex !== currentIndex) {
            showSlide(clickedIndex);
        }

        openOfferModal(slide);
        clearInterval(timerId);
    });

    if (slides.length <= 1) {
        showSlide(currentIndex);
        return;
    }

    const startAutoPlay = () => {
        if (prefersReducedMotion.matches) {
            return;
        }

        clearInterval(timerId);
        timerId = window.setInterval(() => {
            const nextIndex = (currentIndex + 1) % slides.length;
            showSlide(nextIndex);
        }, intervalMs);
    };

    dots.forEach((dot, index) => {
        dot.addEventListener("click", (event) => {
            event.preventDefault();
            showSlide(index);
            startAutoPlay();
        });
    });

    prevButton?.addEventListener("click", (event) => {
        event.preventDefault();
        showSlide(currentIndex - 1);
        startAutoPlay();
    });

    nextButton?.addEventListener("click", (event) => {
        event.preventDefault();
        showSlide(currentIndex + 1);
        startAutoPlay();
    });

    carousel.addEventListener("mouseenter", () => clearInterval(timerId));
    carousel.addEventListener("mouseleave", startAutoPlay);
    carousel.addEventListener("focusin", () => clearInterval(timerId));
    carousel.addEventListener("focusout", startAutoPlay);

    showSlide(currentIndex);
    startAutoPlay();
});

offerModal?.querySelectorAll("[data-offer-modal-close]").forEach((element) => {
    element.addEventListener("click", closeOfferModal);
});

productModal?.querySelectorAll("[data-product-modal-close]").forEach((element) => {
    element.addEventListener("click", closeProductModal);
});

productCards.forEach((card) => {
    card.addEventListener("click", (event) => {
        if (event.target.closest("form") || (event.target.closest("button") && !event.target.closest("[data-product-trigger]"))) {
            return;
        }

        const trigger = event.target.closest("[data-product-trigger], [data-product-card]");
        if (!trigger || !card.contains(trigger)) {
            return;
        }

        event.preventDefault();
        openProductModal(card);
    });
});

quantityControls.forEach((control) => {
    const input = control.querySelector('input[name="quantity"]');
    const decreaseButton = control.querySelector("[data-quantity-decrease]");
    const increaseButton = control.querySelector("[data-quantity-increase]");

    decreaseButton?.addEventListener("click", () => {
        setQuantityValue(input, getQuantityValue(input) - 1);
    });

    increaseButton?.addEventListener("click", () => {
        setQuantityValue(input, getQuantityValue(input) + 1);
    });

    input?.addEventListener("change", () => {
        setQuantityValue(input, getQuantityValue(input));
    });
});

productOptionInputs.forEach((input) => {
    input.addEventListener("change", () => {
        if (productDetailPrice && input.dataset.optionPrice) {
            productDetailPrice.textContent = input.dataset.optionPrice;
        }
        if (productOptionsSubmit) {
            productOptionsSubmit.disabled = !productOptionInputs.some((option) => option.checked);
        }
    });
});

if (productOptionsSubmit && productOptionInputs.length) {
    const checkedOption = productOptionInputs.find((option) => option.checked);
    productOptionsSubmit.disabled = !checkedOption;
    if (checkedOption && productDetailPrice && checkedOption.dataset.optionPrice) {
        productDetailPrice.textContent = checkedOption.dataset.optionPrice;
    }
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeModals();
        setDashboardDrawerOpen(false);
    }
});

dashboardDrawerToggle?.addEventListener("click", () => {
    const isOpen = document.body.classList.contains("is-dashboard-drawer-open");
    setDashboardDrawerOpen(!isOpen);
});

dashboardDrawerClosers.forEach((closer) => {
    closer.addEventListener("click", () => setDashboardDrawerOpen(false));
});

dashboardDrawer?.querySelectorAll("nav a").forEach((link) => {
    link.addEventListener("click", () => setDashboardDrawerOpen(false));
});

dashboardHasOptionsInput?.addEventListener("change", syncDashboardProductOptionsPanel);
syncDashboardProductOptionsPanel();

excelModalOpen?.addEventListener("click", () => setExcelModalOpen(true));
excelModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => setExcelModalOpen(false));
});
checkoutAddressModalOpen?.addEventListener("click", () => setCheckoutAddressModalOpen(true));
checkoutAddressModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => setCheckoutAddressModalOpen(false));
});
if ((excelModal && !excelModal.hidden) || (checkoutAddressModal && !checkoutAddressModal.hidden)) {
    document.body.classList.add("modal-open");
}

homeTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const target = resolveHomeTabTarget(tab);
        if (!target) {
            return;
        }

        setActiveHomeTab(tab.dataset.tabKey || "home");
        target.scrollIntoView({
            behavior: prefersReducedMotion.matches ? "auto" : "smooth",
            block: "start",
        });
    });
});

cartForms.forEach(enhanceCartForm);
enhanceRegisterForm();

syncCartState();
applyStoreHeroProgress(prefersReducedMotion.matches ? 0.92 : 0);
syncActiveHomeTab();

if (homeTabs.length) {
    let tabsTicking = false;

    const scheduleHomeTabSync = () => {
        if (tabsTicking) {
            return;
        }

        tabsTicking = true;
        window.requestAnimationFrame(() => {
            syncActiveHomeTab();
            tabsTicking = false;
        });
    };

    window.addEventListener("scroll", scheduleHomeTabSync, { passive: true });
    window.addEventListener("resize", scheduleHomeTabSync);
}

if (storeHero && heroCartScene && !prefersReducedMotion.matches) {
    let ticking = false;

    const scheduleStoreHero = () => {
        if (ticking) {
            return;
        }

        ticking = true;
        window.requestAnimationFrame(() => {
            animateStoreHeroOnScroll();
            ticking = false;
        });
    };

    window.addEventListener("scroll", scheduleStoreHero, { passive: true });
    window.addEventListener("resize", scheduleStoreHero);
    animateStoreHeroOnScroll();
}
