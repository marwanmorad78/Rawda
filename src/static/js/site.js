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
const productModalDialog = productModal?.querySelector(".product-modal-dialog");
const productModalImageButton = productModal?.querySelector("[data-product-modal-image-button]");
const productModalImage = productModal?.querySelector("[data-product-modal-image]");
const productModalPlaceholder = productModal?.querySelector("[data-product-modal-placeholder]");
const productModalTitle = productModal?.querySelector("[data-product-modal-title]");
const productModalDescription = productModal?.querySelector("[data-product-modal-description]");
const productModalCategory = productModal?.querySelector("[data-product-modal-category]");
const productModalPrice = productModal?.querySelector("[data-product-modal-price]");
const productModalTotal = productModal?.querySelector("[data-product-modal-total]");
const productModalForm = productModal?.querySelector("[data-product-modal-form]");
const productModalOptions = productModal?.querySelector("[data-product-modal-options]");
const productModalCompanies = productModal?.querySelector("[data-product-modal-companies]");
const productModalSubmit = productModal?.querySelector("[data-product-modal-submit]");
const productModalOptionsScroll = productModal?.querySelector(".product-modal-options-scroll");
const productModalLoginPanel = productModal?.querySelector(".product-modal-login-panel");
const productPhotoViewer = document.querySelector("[data-product-photo-viewer]");
const productPhotoViewerImage = productPhotoViewer?.querySelector("[data-product-photo-viewer-image]");
const productPhotoViewerTitle = productPhotoViewer?.querySelector("[data-product-photo-viewer-title]");
const productPhotoViewerClose = productPhotoViewer?.querySelector(".product-photo-viewer-close");

const floatingCart = document.querySelector("[data-floating-cart]");
const floatingCartCount = floatingCart?.querySelector("[data-floating-cart-count]");
const floatingCartTotal = floatingCart?.querySelector("[data-floating-cart-total]");
const floatingCartCargo = floatingCart?.querySelector("[data-floating-cart-cargo]");
const cartForms = Array.from(document.querySelectorAll("[data-cart-form]"));
const cartPage = document.querySelector("[data-cart-page]");
const cartQuantityForms = Array.from(document.querySelectorAll("[data-cart-quantity-form]"));
const cartRemoveForms = Array.from(document.querySelectorAll("[data-cart-remove-form]"));
const cartNoteForms = Array.from(document.querySelectorAll("[data-cart-note-form]"));
const cartNoteOpeners = Array.from(document.querySelectorAll("[data-cart-note-open]"));
const cartNoteDeleteButtons = Array.from(document.querySelectorAll("[data-cart-note-delete]"));
const cartNoteModal = document.querySelector("[data-cart-note-modal]");
const cartNoteModalTitle = cartNoteModal?.querySelector("[data-cart-note-modal-title]");
const cartNoteModalForm = cartNoteModal?.querySelector("[data-cart-note-modal-form]");
const cartNoteModalInput = cartNoteModal?.querySelector("[data-cart-note-input]");
const cartNoteModalClosers = Array.from(document.querySelectorAll("[data-cart-note-close]"));
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
const homeShelfRows = Array.from(document.querySelectorAll("[data-home-shelf-row]"));
const productCards = Array.from(document.querySelectorAll("[data-product-card]"));
const categoryProductSearches = Array.from(document.querySelectorAll("[data-category-product-search]"));
const activeOrderStatusRegions = Array.from(document.querySelectorAll("[data-active-order-status-region]"));
const productOptionInputs = Array.from(
    document.querySelectorAll(
        "[data-product-options] input[name='option_id'], [data-product-company-options] input[name='company_option_id']",
    ),
);
const productDetailPrice = document.querySelector("[data-product-detail-price]");
const productOptionsSubmit = document.querySelector("[data-product-options-submit]");
const quantityControls = Array.from(document.querySelectorAll("[data-quantity-control]"));
const registerForm = document.querySelector("[data-register-form]");
const passwordVisibilityToggles = Array.from(document.querySelectorAll("[data-password-toggle]"));
const syrianPhoneInputs = Array.from(document.querySelectorAll("[data-syrian-phone-input]"));
const syrianPhoneControls = Array.from(document.querySelectorAll("[data-syrian-phone-control]"));
const deliveryAreaGroups = Array.from(document.querySelectorAll("[data-delivery-area-group]"));
const dashboardSubAreaFormsets = Array.from(document.querySelectorAll("[data-dashboard-sub-area-formset]"));
const dashboardDeliveryAreaForms = Array.from(document.querySelectorAll("[data-dashboard-delivery-area-form]"));
const dashboardProductOptionPanels = Array.from(document.querySelectorAll("[data-dashboard-product-options-panel]"));
const dashboardCompanyFormsets = Array.from(document.querySelectorAll("[data-dashboard-company-formset]"));
const expectedTimePresetButtons = Array.from(document.querySelectorAll("[data-time-preset]"));
const siteHeader = document.querySelector(".site-header");
const mobileNavToggle = document.querySelector("[data-mobile-nav-toggle]");
const mobileNavMenu = document.querySelector("[data-mobile-nav-menu]");
const mobileNavMediaQuery = window.matchMedia("(max-width: 560px)");
const dashboardDrawer = document.querySelector("[data-dashboard-drawer]");
const dashboardDrawerToggle = document.querySelector("[data-dashboard-drawer-toggle]");
const dashboardDrawerClosers = Array.from(document.querySelectorAll("[data-dashboard-drawer-close]"));
const dashboardProductOptionsPanel = document.querySelector("[data-dashboard-product-options-panel]");
const dashboardProductCompaniesPanel = document.querySelector("[data-dashboard-product-companies-panel]");
const dashboardProductTypeInput = document.querySelector('select[name="product_type"]');
const dashboardHasOptionsField = document.querySelector("[data-dashboard-has-options-field]");
const dashboardHasOptionsInput = document.querySelector('input[name="has_options"]');
const dashboardProductBasePriceField = document.querySelector("[data-dashboard-product-base-price-field]");
const dashboardProductBasePriceInput = dashboardProductBasePriceField?.querySelector("input, select, textarea");
const excelModal = document.querySelector("[data-excel-modal]");
const excelModalOpen = document.querySelector("[data-excel-modal-open]");
const excelModalClosers = Array.from(document.querySelectorAll("[data-excel-modal-close]"));
const orderModals = Array.from(document.querySelectorAll("[data-order-modal]"));
const orderModalOpeners = Array.from(document.querySelectorAll("[data-order-modal-open]"));
const orderModalClosers = Array.from(document.querySelectorAll("[data-order-modal-close]"));
const checkoutAddressModals = Array.from(document.querySelectorAll("[data-checkout-address-modal]"));
const checkoutAddressModalOpeners = Array.from(document.querySelectorAll("[data-checkout-address-modal-open]"));
const checkoutAddressModalClosers = Array.from(document.querySelectorAll("[data-checkout-address-modal-close]"));
const checkoutAddressOptions = Array.from(document.querySelectorAll("[data-checkout-address-option]"));
const checkoutDeliveryFee = document.querySelector("[data-checkout-delivery-fee]");
const checkoutGrandTotal = document.querySelector("[data-checkout-grand-total]");
const checkoutFlow = document.querySelector("[data-checkout-flow]");
const checkoutServiceOptions = Array.from(document.querySelectorAll("[data-checkout-service-option]"));
const checkoutAddressPanel = document.querySelector("[data-checkout-address-panel]");
const checkoutConfirmForm = document.querySelector("[data-checkout-confirm-form]");
const checkoutConfirmSubmit = document.querySelector("[data-checkout-confirm-submit]");
const checkoutConfirmModal = document.querySelector("[data-checkout-confirm-modal]");
const checkoutConfirmClosers = Array.from(document.querySelectorAll("[data-checkout-confirm-close]"));
const checkoutConfirmApprove = document.querySelector("[data-checkout-confirm-approve]");
const dashboardColumnFilters = Array.from(document.querySelectorAll("[data-column-filter]"));
const confirmationForms = Array.from(document.querySelectorAll("form[data-confirm-submit]"));
const newOrderAlert = document.querySelector("[data-new-order-alert]");
const newOrderSound = document.querySelector("#newOrderSound");
const newOrderEnableButton = document.querySelector("[data-new-order-enable]");
const newOrderNumber = newOrderAlert?.querySelector("[data-new-order-number]");
const newOrderCustomer = newOrderAlert?.querySelector("[data-new-order-customer]");
const newOrderType = newOrderAlert?.querySelector("[data-new-order-type]");
const newOrderTotal = newOrderAlert?.querySelector("[data-new-order-total]");
const newOrderOpenButton = newOrderAlert?.querySelector("[data-new-order-open]");
const newOrderSilenceButtons = Array.from(document.querySelectorAll("[data-new-order-silence]"));

const cartState = {
    count: Number.parseInt(floatingCart?.dataset.cartCount || "0", 10) || 0,
    total: floatingCart?.dataset.cartTotal || "0",
};
const newOrderAlertState = {
    activeOrder: null,
    audioEnabled: false,
    isPolling: false,
    knownOrderIds: new Set(),
    queue: [],
};
const ARABIC_NAME_PATTERN = /^[\u0621-\u064A\u064B-\u065F]+(?:\s+[\u0621-\u064A\u064B-\u065F]+)*$/;
let lockedBodyScrollY = 0;
let lockedRootScrollBehavior = "";
let lockedBodyScrollRestoreTimer = null;
let productModalUnitPriceText = "";
let activeCartNoteCard = null;
const PRODUCT_MODAL_HISTORY_KEY = "rawdaProductModal";

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
const tabTargetCache = new WeakMap();

const getCookieValue = (name) => {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    const prefix = `${name}=`;
    const cookie = cookies.find((item) => item.trim().startsWith(prefix));
    if (!cookie) {
        return "";
    }
    return decodeURIComponent(cookie.trim().slice(prefix.length));
};

const getCsrfToken = () =>
    getCookieValue("csrftoken") || document.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";

const syncViewportHeightVariable = () => {
    const viewportHeight = window.visualViewport?.height || window.innerHeight;
    const viewportOffsetTop = window.visualViewport?.offsetTop || 0;
    document.documentElement.style.setProperty("--app-viewport-height", `${Math.round(viewportHeight)}px`);
    document.documentElement.style.setProperty("--app-viewport-offset-top", `${Math.round(viewportOffsetTop)}px`);
};

const getAnyOpenModal = () =>
    Boolean(
        (siteHeader?.classList.contains("is-mobile-nav-open") && mobileNavMediaQuery.matches) ||
            (offerModal && !offerModal.hidden) ||
            (productModal && !productModal.hidden) ||
            (productPhotoViewer && !productPhotoViewer.hidden) ||
            (excelModal && !excelModal.hidden) ||
            (cartNoteModal && !cartNoteModal.hidden) ||
            (checkoutConfirmModal && !checkoutConfirmModal.hidden) ||
            orderModals.some((modal) => !modal.hidden) ||
            checkoutAddressModals.some((modal) => !modal.hidden),
    );

const setBodyScrollLock = (isLocked) => {
    const isAlreadyLocked = document.body.classList.contains("modal-open");

    if (isLocked && !isAlreadyLocked) {
        window.clearTimeout(lockedBodyScrollRestoreTimer);
        syncViewportHeightVariable();
        lockedBodyScrollY = window.scrollY || document.documentElement.scrollTop || 0;
        lockedRootScrollBehavior = document.documentElement.style.scrollBehavior;
        document.documentElement.style.setProperty("scroll-behavior", "auto", "important");
        document.body.classList.add("modal-open");
        document.body.style.position = "fixed";
        document.body.style.top = `-${lockedBodyScrollY}px`;
        document.body.style.left = "0";
        document.body.style.right = "0";
        document.body.style.width = "100%";
        return;
    }

    if (!isLocked && isAlreadyLocked) {
        const restoreY = lockedBodyScrollY;
        document.body.classList.remove("modal-open");
        document.body.style.position = "";
        document.body.style.top = "";
        document.body.style.left = "";
        document.body.style.right = "";
        document.body.style.width = "";

        const restoreScrollPosition = () => {
            try {
                window.scrollTo({
                    left: 0,
                    top: restoreY,
                    behavior: "instant",
                });
            } catch (error) {
                window.scrollTo(0, restoreY);
            }
        };

        restoreScrollPosition();
        window.requestAnimationFrame(() => {
            restoreScrollPosition();
            window.requestAnimationFrame(restoreScrollPosition);
        });
        lockedBodyScrollRestoreTimer = window.setTimeout(() => {
            restoreScrollPosition();
            document.documentElement.style.scrollBehavior = lockedRootScrollBehavior;
        }, 120);
    }
};

const registerMessages = {
    en: {
        required: (label) => `${label} is required.`,
        passwordNumeric: "Password cannot be entirely numeric.",
        passwordMismatch: "Passwords do not match.",
        phoneInvalid: "يرجى التأكد من ادخال رقم صحيح",
        phoneTaken: "This phone number is already registered.",
        nameArabicOnly: "Please enter the full name in Arabic only.",
        fixBeforeSubmit: "Please fix the highlighted information.",
    },
    ar: {
        required: (label) => `${label} مطلوب.`,
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

const setMobileNavOpen = (isOpen) => {
    if (!siteHeader || !mobileNavToggle || !mobileNavMenu) {
        return;
    }

    siteHeader.classList.toggle("is-mobile-nav-open", isOpen);
    mobileNavToggle.setAttribute("aria-expanded", String(isOpen));
    if (mobileNavMediaQuery.matches) {
        mobileNavMenu.setAttribute("aria-hidden", String(!isOpen));
    } else {
        mobileNavMenu.removeAttribute("aria-hidden");
    }
    syncModalOpenState();
};

const syncDashboardProductOptionsPanel = () => {
    if (!dashboardHasOptionsInput && !dashboardProductTypeInput) {
        return;
    }
    const isCompanyGrouped = dashboardProductTypeInput?.value === "company_grouped";
    const hasOptions = Boolean(dashboardHasOptionsInput?.checked) && !isCompanyGrouped;
    if (dashboardHasOptionsInput && isCompanyGrouped) {
        dashboardHasOptionsInput.checked = false;
    }
    if (dashboardHasOptionsField) {
        dashboardHasOptionsField.hidden = isCompanyGrouped;
    }
    if (dashboardProductOptionsPanel) {
        dashboardProductOptionsPanel.hidden = !hasOptions;
    }
    if (dashboardProductCompaniesPanel) {
        dashboardProductCompaniesPanel.hidden = !isCompanyGrouped;
    }
    if (dashboardProductBasePriceField) {
        dashboardProductBasePriceField.hidden = hasOptions || isCompanyGrouped;
    }
    if (dashboardProductBasePriceInput) {
        dashboardProductBasePriceInput.disabled = hasOptions || isCompanyGrouped;
        dashboardProductBasePriceInput.required = !hasOptions && !isCompanyGrouped;
    }
};

const setExcelModalOpen = (isOpen) => {
    if (!excelModal) {
        return;
    }
    excelModal.hidden = !isOpen;
    syncModalOpenState();
};

const setCartNoteModalOpen = (isOpen) => {
    if (!cartNoteModal) {
        return;
    }
    cartNoteModal.hidden = !isOpen;
    syncModalOpenState();
};

const syncModalOpenState = () => {
    setBodyScrollLock(getAnyOpenModal());
};

const setCheckoutAddressModalOpen = (isOpen, modal = checkoutAddressModals[0]) => {
    if (!modal) {
        return;
    }
    modal.hidden = !isOpen;
    syncModalOpenState();
};

const closeCheckoutAddressModals = () => {
    checkoutAddressModals.forEach((modal) => {
        modal.hidden = true;
    });
    syncModalOpenState();
};

const setCheckoutConfirmModalOpen = (isOpen) => {
    if (!checkoutConfirmModal) {
        return;
    }
    checkoutConfirmModal.hidden = !isOpen;
    syncModalOpenState();
};

const setOrderModalOpen = (isOpen, modal) => {
    if (!modal) {
        return;
    }
    modal.hidden = !isOpen;
    syncModalOpenState();
};

const closeOrderModals = () => {
    orderModals.forEach((modal) => {
        modal.hidden = true;
    });
    syncModalOpenState();
};

const getQuantityValue = (input) => {
    const minimum = Number(input?.min || 1);
    const current = Number(input?.value || minimum);
    return Math.max(Number.isFinite(current) ? current : minimum, minimum);
};

const setQuantityValue = (input, value) => {
    if (!input) {
        return;
    }

    const minimum = Number(input.min || 1);
    const maximum = input.max ? Number(input.max) : Number.POSITIVE_INFINITY;
    const step = Number(input.step || 1);
    const numericValue = Number(value);
    const boundedValue = Math.min(
        Math.max(Number.isFinite(numericValue) ? numericValue : minimum, minimum),
        maximum,
    );
    const steppedValue = minimum + Math.round((boundedValue - minimum) / step) * step;
    input.value = String(Math.min(Math.max(steppedValue, minimum), maximum));

    const control = input.closest("[data-quantity-control], [data-cart-quantity-stepper]");
    const display = control?.querySelector("[data-quantity-display]");
    const isWeightBased = Boolean(control?.hasAttribute("data-weight-control"));
    if (display) {
        const quantity = Number(input.value);
        const isArabic = document.documentElement.lang === "ar";
        display.textContent = quantity < 1
            ? `${Math.round(quantity * 1000)} ${isArabic ? "غ" : "g"}`
            : `${Number(quantity.toFixed(1))} ${isArabic ? "كغ" : "kg"}`;
    }
    control?.querySelector("[data-quantity-decrease], [data-cart-quantity-decrease]")
        ?.toggleAttribute("disabled", isWeightBased && Number(input.value) <= minimum);
    control?.querySelector("[data-quantity-increase], [data-cart-quantity-increase]")
        ?.toggleAttribute("disabled", Number(input.value) >= maximum);
};

const normalizePriceText = (value) =>
    String(value || "")
        .replace(/[\u0660-\u0669]/g, (digit) => String(digit.charCodeAt(0) - 0x0660))
        .replace(/[\u06F0-\u06F9]/g, (digit) => String(digit.charCodeAt(0) - 0x06F0));

const formatDisplayPriceTotal = (displayPrice, quantity, numericUnitPrice = null, showEstimate = false) => {
    const priceText = String(displayPrice || "").trim();
    if (!priceText) {
        return "";
    }

    const normalized = normalizePriceText(priceText);
    const match = normalized.match(/\d[\d.,\u066C\u066B]*/);
    if (!match) {
        return priceText;
    }

    const numericValue = numericUnitPrice === null
        ? Number.parseInt(match[0].replace(/[^\d]/g, ""), 10)
        : Number(numericUnitPrice);
    if (!Number.isFinite(numericValue)) {
        return priceText;
    }

    const language = document.documentElement.lang || undefined;
    const formatter = new Intl.NumberFormat(language);
    const total = Math.round(numericValue * Math.max(quantity, 0));
    const formattedTotal = showEstimate
        ? `${formatter.format(total)} ~ ${formatter.format(Math.round(numericValue * (quantity + 0.1)))}`
        : formatter.format(total);
    const originalNumberText = priceText.slice(match.index, match.index + match[0].length);
    return priceText.replace(originalNumberText, formattedTotal);
};

const syncProductModalTotal = () => {
    if (!productModalTotal || !productModalForm) {
        return;
    }

    const quantityInput = productModalForm.querySelector('input[name="quantity"]');
    const selectedOption = productModalForm.querySelector(
        'input[name="option_id"]:checked, input[name="company_option_id"]:checked',
    );
    const displayPrice = selectedOption?.dataset.optionPrice || productModalUnitPriceText || productModalPrice?.textContent || "";
    const unitPrice = selectedOption?.dataset.optionUnitPrice || productModalForm.dataset.productUnitPrice || null;
    const isWeightBased = productModalForm.dataset.soldByWeight === "true";
    productModalTotal.textContent = formatDisplayPriceTotal(
        displayPrice,
        quantityInput ? getQuantityValue(quantityInput) : 1,
        unitPrice,
        isWeightBased,
    );
};

const syncProductModalSubmitState = () => {
    if (!productModalSubmit || !productModalForm) {
        return;
    }

    const requiresSelection = productModalDialog?.classList.contains("has-options");
    const selectedOption = productModalForm.querySelector(
        'input[name="option_id"]:checked:not(:disabled), input[name="company_option_id"]:checked:not(:disabled)',
    );
    productModalSubmit.disabled = Boolean(requiresSelection && !selectedOption);
};

const resetProductModalMedia = () => {
    if (productModalImageButton) {
        productModalImageButton.hidden = true;
        productModalImageButton.removeAttribute("aria-label");
    }
    if (productModalImage) {
        productModalImage.onerror = null;
        productModalImage.removeAttribute("src");
        productModalImage.removeAttribute("srcset");
        productModalImage.alt = "";
        productModalImage.hidden = true;
    }

    if (productModalPlaceholder) {
        productModalPlaceholder.textContent = "";
        productModalPlaceholder.hidden = false;
    }
};

const closeProductPhotoViewer = () => {
    if (!productPhotoViewer) {
        return;
    }

    productPhotoViewer.hidden = true;
    if (productPhotoViewerImage) {
        productPhotoViewerImage.removeAttribute("src");
        productPhotoViewerImage.alt = "";
    }
    if (productPhotoViewerTitle) {
        productPhotoViewerTitle.textContent = "";
    }
    syncModalOpenState();

    if (productModal && !productModal.hidden && productModalImageButton && !productModalImageButton.hidden) {
        productModalImageButton.focus({ preventScroll: true });
    }
};

const openProductPhotoViewer = () => {
    const imageSource = productModalImage?.currentSrc || productModalImage?.src;
    if (!productPhotoViewer || !productPhotoViewerImage || !imageSource || productModalImage?.hidden) {
        return;
    }

    const title = productModalTitle?.textContent?.trim() || productModalImage.alt || "";
    productPhotoViewerImage.src = imageSource;
    productPhotoViewerImage.alt = productModalImage.alt || title;
    if (productPhotoViewerTitle) {
        productPhotoViewerTitle.textContent = title;
    }
    productPhotoViewer.hidden = false;
    syncModalOpenState();
    productPhotoViewerClose?.focus({ preventScroll: true });
};

const resetProductModalContent = () => {
    resetProductModalMedia();
    productModalDialog?.classList.remove(
        "has-options",
        "has-no-options",
        "has-few-options",
        "has-many-options",
        "has-company-groups",
        "requires-login",
    );
    if (productModalTitle) {
        productModalTitle.textContent = "";
    }
    if (productModalDescription) {
        productModalDescription.textContent = "";
        productModalDescription.hidden = true;
    }
    if (productModalCategory) {
        productModalCategory.textContent = "";
        productModalCategory.hidden = true;
    }
    if (productModalPrice) {
        productModalPrice.textContent = "";
    }
    if (productModalTotal) {
        productModalTotal.textContent = "";
    }
    if (productModalOptions) {
        productModalOptions.querySelectorAll(".product-option-card").forEach((option) => option.remove());
        productModalOptions.hidden = true;
    }
    if (productModalCompanies) {
        productModalCompanies.querySelectorAll(".product-company-card").forEach((company) => company.remove());
        productModalCompanies.hidden = true;
    }
    if (productModalOptionsScroll) {
        productModalOptionsScroll.hidden = true;
        productModalOptionsScroll.classList.remove("has-many-options");
        productModalOptionsScroll.scrollTop = 0;
    }
    if (productModalSubmit) {
        productModalSubmit.disabled = false;
    }
};

const normalizeLabel = (value) =>
    String(value || "")
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^\p{L}\p{N}]+/gu, " ")
        .trim();

const enhanceCategoryProductSearch = (form) => {
    const input = form?.querySelector("[data-category-product-search-input]");
    const section = form?.closest("[data-category-product-section]");
    const cards = Array.from(section?.querySelectorAll("[data-product-card]") || []);
    const emptyMessage = section?.querySelector("[data-category-product-search-empty]");

    if (!input || !cards.length) {
        return;
    }

    const searchableTextByCard = new Map(
        cards.map((card) => [
            card,
            normalizeLabel(
                [
                    card.dataset.productTitle,
                    card.dataset.productDescription,
                    card.dataset.productCategory,
                    card.dataset.productPrice,
                ].join(" "),
            ),
        ]),
    );

    const filterProducts = () => {
        const query = normalizeLabel(input.value);
        let visibleCount = 0;

        cards.forEach((card) => {
            const isMatch = !query || searchableTextByCard.get(card).includes(query);
            card.hidden = !isMatch;
            if (isMatch) {
                visibleCount += 1;
            }
        });

        if (emptyMessage) {
            emptyMessage.hidden = !query || visibleCount > 0;
        }
    };

    form.addEventListener("submit", (event) => event.preventDefault());
    input.addEventListener("input", filterProducts);
    filterProducts();
};

const enhanceHomeShelfRow = (row) => {
    const scroller = row.closest("[data-home-shelf-scroller]");
    if (!scroller) {
        console.warn("No scroller found for row:", row);
        return;
    }

    console.log("Scroller found:", {
        scrollWidth: scroller.scrollWidth,
        clientWidth: scroller.clientWidth,
        hasOverflow: scroller.scrollWidth > scroller.clientWidth
    });

    const getMaxScroll = () => Math.max(0, scroller.scrollWidth - scroller.clientWidth);
    const getStep = () => Math.max(scroller.clientWidth * 0.82, 260);
    const scrollToRightEdge = () => {
        scroller.scrollLeft = getMaxScroll();
    };

    const syncButtons = () => {
        const maxScroll = getMaxScroll();
        const hasOverflow = maxScroll > 2;
        const currentScroll = scroller.scrollLeft;

        row.classList.toggle("has-overflow", hasOverflow);
    };

    scroller.addEventListener("scroll", syncButtons, { passive: true });
    window.addEventListener("resize", syncButtons);

    scroller.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
            return;
        }

        event.preventDefault();
        scroller.scrollBy({ left: event.key === "ArrowLeft" ? -getStep() : getStep(), behavior: "smooth" });
    });

    scroller.addEventListener(
        "wheel",
        (event) => {
            const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;

            if (!delta || getMaxScroll() <= 2) {
                return;
            }

            event.preventDefault();
            scroller.scrollBy({ left: delta, behavior: "auto" });
        },
        { passive: false },
    );

    window.requestAnimationFrame(() => {
        scrollToRightEdge();
        syncButtons();
    });
};

const enhanceActiveOrderStatusRegion = (region) => {
    const url = region.dataset.activeOrderStatusUrl;
    if (!url) {
        return;
    }

    const refresh = async () => {
        if (document.visibilityState === "hidden") {
            return;
        }

        try {
            const response = await window.fetch(url, {
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            if (!response.ok) {
                return;
            }
            const payload = await response.json();
            if (payload.has_active_order && payload.html) {
                const target = region.classList.contains("active-order-home")
                    ? region.querySelector(".container") || region
                    : region;
                target.innerHTML = payload.html;
                enhanceBusyCountdowns(target);
                region.hidden = false;
                return;
            }
            region.classList.add("is-order-complete");
            window.setTimeout(() => {
                region.hidden = true;
                region.innerHTML = "";
            }, 260);
        } catch (error) {
            return;
        }
    };

    window.setInterval(refresh, 25000);
};

const stopNewOrderAlarm = () => {
    if (!newOrderSound) {
        return;
    }
    newOrderSound.pause();
    newOrderSound.currentTime = 0;
};

const playNewOrderAlarm = async () => {
    if (!newOrderSound || !newOrderAlertState.audioEnabled) {
        return;
    }

    try {
        newOrderSound.currentTime = 0;
        await newOrderSound.play();
    } catch (error) {
        return;
    }
};

const setNewOrderEnableButtonActive = () => {
    if (!newOrderEnableButton) {
        return;
    }
    newOrderEnableButton.classList.add("is-enabled");
    newOrderEnableButton.textContent = newOrderEnableButton.dataset.enabledLabel || newOrderEnableButton.textContent;
};

const enableNewOrderAudio = async () => {
    newOrderAlertState.audioEnabled = true;
    try {
        window.sessionStorage?.setItem("rawdaNewOrderAudioEnabled", "true");
    } catch (error) {
        // Alerts still work if browser storage is unavailable.
    }
    setNewOrderEnableButtonActive();

    if (!newOrderSound) {
        return;
    }

    const previousVolume = newOrderSound.volume;
    try {
        newOrderSound.volume = 0;
        await newOrderSound.play();
        stopNewOrderAlarm();
    } catch (error) {
        return;
    } finally {
        newOrderSound.volume = previousVolume;
    }
};

const renderNewOrderAlert = (order) => {
    if (!newOrderAlert || !order) {
        return;
    }
    newOrderAlertState.activeOrder = order;
    if (newOrderNumber) {
        newOrderNumber.textContent = order.order_number || "";
    }
    if (newOrderCustomer) {
        newOrderCustomer.textContent = order.customer_name || "";
    }
    if (newOrderType) {
        newOrderType.textContent = order.order_type || "";
    }
    if (newOrderTotal) {
        newOrderTotal.textContent = order.total || "";
    }
    newOrderAlert.hidden = false;
    document.body.classList.add("is-new-order-alert-open");
    playNewOrderAlarm();
};

const showNextNewOrderAlert = () => {
    if (newOrderAlertState.activeOrder || !newOrderAlertState.queue.length) {
        return;
    }
    renderNewOrderAlert(newOrderAlertState.queue.shift());
};

const enqueueNewOrders = (orders) => {
    if (!Array.isArray(orders)) {
        return;
    }

    orders.forEach((order) => {
        const orderId = String(order.order_id || "");
        if (!orderId || newOrderAlertState.knownOrderIds.has(orderId)) {
            return;
        }
        newOrderAlertState.knownOrderIds.add(orderId);
        newOrderAlertState.queue.push(order);
    });
    showNextNewOrderAlert();
};

const acknowledgeNewOrder = async (order) => {
    if (!newOrderAlert || !order?.order_id) {
        return false;
    }

    const formData = new FormData();
    formData.set("order_id", order.order_id);
    const csrfToken = getCsrfToken();
    const headers = {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
    };
    if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
    }

    try {
        const response = await window.fetch(newOrderAlert.dataset.checkUrl, {
            method: "POST",
            body: formData,
            headers,
        });
        return response.ok;
    } catch (error) {
        return false;
    }
};

const closeNewOrderAlert = () => {
    stopNewOrderAlarm();
    if (newOrderAlert) {
        newOrderAlert.hidden = true;
    }
    document.body.classList.remove("is-new-order-alert-open");
    newOrderAlertState.activeOrder = null;
};

const silenceNewOrderAlert = async () => {
    const order = newOrderAlertState.activeOrder;
    closeNewOrderAlert();
    await acknowledgeNewOrder(order);
    showNextNewOrderAlert();
};

const openNewOrder = async () => {
    const order = newOrderAlertState.activeOrder;
    if (!order) {
        return;
    }
    closeNewOrderAlert();
    await acknowledgeNewOrder(order);
    if (order.detail_url) {
        window.location.href = order.detail_url;
    }
};

const pollNewOrders = async () => {
    if (!newOrderAlert || !newOrderAlert.dataset.checkUrl || document.visibilityState === "hidden") {
        return;
    }
    if (newOrderAlertState.isPolling) {
        return;
    }

    newOrderAlertState.isPolling = true;
    try {
        const response = await window.fetch(newOrderAlert.dataset.checkUrl, {
            headers: {
                Accept: "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        if (!response.ok) {
            return;
        }
        const payload = await response.json();
        enqueueNewOrders(payload.orders);
    } catch (error) {
        return;
    } finally {
        newOrderAlertState.isPolling = false;
    }
};

const enhanceNewOrderAlerts = () => {
    if (!newOrderAlert) {
        return;
    }

    try {
        if (window.sessionStorage?.getItem("rawdaNewOrderAudioEnabled") === "true") {
            newOrderAlertState.audioEnabled = true;
            setNewOrderEnableButtonActive();
        }
    } catch (error) {
        // Alerts still work if browser storage is unavailable.
    }

    newOrderEnableButton?.addEventListener("click", enableNewOrderAudio);
    newOrderOpenButton?.addEventListener("click", openNewOrder);
    newOrderSilenceButtons.forEach((button) => {
        button.addEventListener("click", silenceNewOrderAlert);
    });

    window.setInterval(pollNewOrders, 10000);
    window.setTimeout(pollNewOrders, 1200);
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") {
            pollNewOrders();
        }
    });
};

const enhanceBusyCountdowns = (scope = document) => {
    scope.querySelectorAll("[data-busy-countdown]").forEach((element) => {
        if (element.dataset.busyCountdownEnhanced === "true") {
            return;
        }
        element.dataset.busyCountdownEnhanced = "true";

        let remainingSeconds = Number.parseInt(element.dataset.busyRemainingSeconds || "0", 10);
        const template = element.dataset.busyMessageTemplate || "";
        const render = () => {
            const minutes = Math.max(Math.ceil(remainingSeconds / 60), 0);
            element.textContent = template.replace("{minutes}", String(minutes));
            if (remainingSeconds <= 0) {
                window.setTimeout(() => window.location.reload(), 700);
            }
            remainingSeconds -= 1;
        };

        render();
        window.setInterval(render, 1000);
    });
};

const enhanceDashboardCenterCountdown = () => {
    const element = document.querySelector("[data-dashboard-center-countdown]");
    if (!element) {
        return;
    }

    let remainingSeconds = Number.parseInt(element.dataset.remainingSeconds || "0", 10);
    const label = element.dataset.label || "";

    const render = () => {
        const safeSeconds = Math.max(remainingSeconds, 0);
        const minutes = Math.floor(safeSeconds / 60);
        const seconds = String(safeSeconds % 60).padStart(2, "0");
        element.textContent = `${label} ${minutes}:${seconds}`;
        if (remainingSeconds <= 0) {
            window.setTimeout(() => window.location.reload(), 700);
            return;
        }
        remainingSeconds -= 1;
    };

    render();
    window.setInterval(render, 1000);
};

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

const enhancePasswordVisibilityToggle = (toggle) => {
    const field = toggle?.closest("[data-password-field]");
    const input = field?.querySelector('input[type="password"], input[type="text"]');
    if (!toggle || !input) {
        return;
    }

    const showLabel = toggle.dataset.showLabel || "Show password";
    const hideLabel = toggle.dataset.hideLabel || "Hide password";

    toggle.addEventListener("click", () => {
        const shouldShow = input.type === "password";
        input.type = shouldShow ? "text" : "password";
        toggle.classList.toggle("is-visible", shouldShow);
        toggle.setAttribute("aria-label", shouldShow ? hideLabel : showLabel);
        toggle.setAttribute("title", shouldShow ? hideLabel : showLabel);
        input.focus();
    });
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

const addFormsetRow = ({ rowsContainer, emptyTemplate, totalFormsInput, token = "__prefix__", extraReplacements = {} }) => {
    if (!rowsContainer || !emptyTemplate || !totalFormsInput) {
        return null;
    }

    const nextIndex = Number.parseInt(totalFormsInput.value || "0", 10) || 0;
    let templateMarkup = emptyTemplate.innerHTML.replaceAll(token, String(nextIndex));
    Object.entries(extraReplacements).forEach(([key, value]) => {
        templateMarkup = templateMarkup.replaceAll(key, String(value));
    });
    templateMarkup = templateMarkup.trim();
    if (!templateMarkup) {
        return null;
    }

    rowsContainer.insertAdjacentHTML("beforeend", templateMarkup);
    totalFormsInput.value = String(nextIndex + 1);
    return rowsContainer.lastElementChild;
};

const enhanceDashboardProductOptionsPanel = (panel) => {
    const rowsContainer = panel.querySelector("[data-dashboard-option-rows]");
    const addButton = panel.querySelector("[data-dashboard-add-option]");
    const emptyTemplate = panel.querySelector("[data-dashboard-option-empty-form]");
    const totalFormsInput = panel.querySelector('input[name$="-TOTAL_FORMS"]');

    addButton?.addEventListener("click", () => {
        addFormsetRow({ rowsContainer, emptyTemplate, totalFormsInput });
    });
};

const enhanceDashboardCompanyOptionControls = (scope) => {
    scope.querySelectorAll("[data-dashboard-add-company-option]").forEach((button) => {
        button.addEventListener("click", () => {
            const optionsPanel = button.closest(".dashboard-company-options");
            const rowsContainer = optionsPanel?.querySelector("[data-dashboard-company-option-rows]");
            const emptyTemplate = optionsPanel?.querySelector("[data-dashboard-company-option-empty-form]");
            const totalFormsInput = optionsPanel?.querySelector('input[name$="-TOTAL_FORMS"]');
            addFormsetRow({ rowsContainer, emptyTemplate, totalFormsInput });
        });
    });
};

const enhanceDashboardCompanyFormset = (formset) => {
    const rowsContainer = formset.querySelector("[data-dashboard-company-rows]");
    const addButton = formset.querySelector("[data-dashboard-add-company]");
    const emptyTemplate = formset.querySelector("[data-dashboard-company-empty-form]");
    const totalFormsInput = formset.querySelector('input[name="companies-TOTAL_FORMS"]');

    enhanceDashboardCompanyOptionControls(formset);

    addButton?.addEventListener("click", () => {
        if (!rowsContainer || !emptyTemplate || !totalFormsInput) {
            return;
        }
        const nextIndex = Number.parseInt(totalFormsInput.value || "0", 10) || 0;
        const templateMarkup = emptyTemplate.innerHTML
            .replaceAll("__company_index__", String(nextIndex))
            .replaceAll("companies-__prefix__", `companies-${nextIndex}`)
            .replaceAll("id_companies-__prefix__", `id_companies-${nextIndex}`)
            .trim();

        if (!templateMarkup) {
            return;
        }

        rowsContainer.insertAdjacentHTML("beforeend", templateMarkup);
        totalFormsInput.value = String(nextIndex + 1);
        const row = rowsContainer.lastElementChild;
        if (row) {
            enhanceDashboardCompanyOptionControls(row);
        }
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

const getFieldValidationTarget = (field) =>
    field?.closest("[data-syrian-phone-control]") || field?.closest("[data-password-field]") || field;

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
    syncModalOpenState();
};

const closeOfferModal = (event) => {
    event?.preventDefault();
    event?.stopPropagation();

    if (!offerModal) {
        return;
    }

    offerModal.hidden = true;
    syncModalOpenState();
};

const buildProductCompanyCard = (companyNode, basePrice) => {
    const card = document.createElement("article");
    card.className = "product-company-card";

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "product-company-summary";
    toggle.setAttribute("aria-expanded", "false");

    const logo = document.createElement("span");
    logo.className = "product-company-logo";
    const logoUrl = companyNode.dataset.companyLogo || "";
    const companyName = companyNode.dataset.companyName || "";
    if (logoUrl) {
        const image = document.createElement("img");
        image.src = logoUrl;
        image.alt = companyName;
        image.addEventListener("error", () => {
            image.remove();
            const placeholder = document.createElement("span");
            placeholder.textContent = companyName.slice(0, 1);
            logo.append(placeholder);
        }, { once: true });
        logo.append(image);
    } else {
        const placeholder = document.createElement("span");
        placeholder.textContent = companyName.slice(0, 1);
        logo.append(placeholder);
    }

    const name = document.createElement("strong");
    name.textContent = companyName;

    const arrow = document.createElement("span");
    arrow.className = "product-company-arrow";
    arrow.setAttribute("aria-hidden", "true");

    const optionsWrap = document.createElement("div");
    optionsWrap.className = "product-company-options";
    optionsWrap.hidden = true;

    Array.from(companyNode.querySelectorAll("[data-company-option-id]")).forEach((optionNode) => {
        const label = document.createElement("label");
        label.className = "product-option-card product-company-option-row";

        const input = document.createElement("input");
        input.type = "radio";
        input.name = "company_option_id";
        input.value = optionNode.dataset.companyOptionId || "";
        input.required = true;
        input.dataset.optionPrice = optionNode.dataset.companyOptionPrice || "";
        input.dataset.optionUnitPrice = optionNode.dataset.companyOptionUnitPrice || "";
        input.disabled = optionNode.dataset.companyOptionAvailable === "false";

        const mark = document.createElement("span");
        mark.className = "choice-mark choice-mark-radio";
        mark.setAttribute("aria-hidden", "true");

        const copy = document.createElement("span");
        copy.className = "choice-copy";
        const optionName = document.createElement("strong");
        optionName.textContent = optionNode.dataset.companyOptionName || "";
        const optionPrice = document.createElement("small");
        optionPrice.textContent = optionNode.dataset.companyOptionPrice || "";
        copy.append(optionName, optionPrice);
        if (input.disabled) {
            const unavailable = document.createElement("em");
            unavailable.textContent = document.documentElement.lang === "ar" ? "غير متوفر حالياً" : "Unavailable now";
            copy.append(unavailable);
            label.classList.add("is-unavailable");
        }

        input.addEventListener("change", () => {
            productModalUnitPriceText = input.dataset.optionPrice || basePrice;
            if (productModalPrice) {
                productModalPrice.textContent = productModalUnitPriceText;
            }
            syncProductModalSubmitState();
            syncProductModalTotal();
        });

        label.append(input, mark, copy);
        optionsWrap.append(label);
    });

    if (!optionsWrap.querySelector('input[name="company_option_id"]:not(:disabled)')) {
        const empty = document.createElement("p");
        empty.className = "product-company-empty";
        empty.textContent = document.documentElement.lang === "ar" ? "لا توجد خيارات متوفرة حالياً" : "No options are currently available.";
        optionsWrap.append(empty);
    }

    toggle.addEventListener("click", () => {
        const isOpen = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!isOpen));
        card.classList.toggle("is-open", !isOpen);
        optionsWrap.hidden = isOpen;
    });

    toggle.append(logo, name, arrow);
    card.append(toggle, optionsWrap);
    return card;
};

const openProductModal = (card) => {
    if (!productModal || !productModalTitle || !productModalPrice || !productModalForm) {
        return;
    }
    if (card.dataset.productAvailable === "false") {
        return;
    }

    const title = card.dataset.productTitle || "";
    const description = card.dataset.productDescription || "";
    const category = card.dataset.productCategory || "";
    const price = card.dataset.productPrice || "";
    const unitPrice = card.dataset.productUnitPrice || "";
    const isWeightBased = card.dataset.productSoldByWeight === "true";
    const image = card.dataset.productImage || "";
    const action = card.dataset.productAction || "";
    const productType = card.dataset.productType || "normal";
    const isCompanyGrouped = productType === "company_grouped";

    syncViewportHeightVariable();
    resetProductModalContent();
    productModalUnitPriceText = price;
    productModalTitle.textContent = title;
    productModalPrice.textContent = price;
    productModalForm.action = action;
    productModalForm.dataset.cartItemTitle = title;
    productModalForm.dataset.cartItemImage = image;
    productModalForm.dataset.productUnitPrice = unitPrice;
    productModalForm.dataset.soldByWeight = String(isWeightBased);
    const quantityInput = productModalForm.querySelector('input[name="quantity"]');
    const quantityControl = quantityInput?.closest("[data-quantity-control]");
    const quantityDisplay = quantityControl?.querySelector("[data-quantity-display]");
    if (quantityInput) {
        quantityInput.type = isWeightBased ? "hidden" : "number";
        quantityInput.min = isWeightBased ? "0.5" : "1";
        quantityInput.max = isWeightBased ? "10" : "";
        quantityInput.step = isWeightBased ? "0.5" : "1";
        quantityInput.inputMode = isWeightBased ? "" : "numeric";
    }
    quantityControl?.toggleAttribute("data-weight-control", isWeightBased);
    if (quantityDisplay) {
        quantityDisplay.hidden = !isWeightBased;
    }
    setQuantityValue(quantityInput, isWeightBased ? 0.5 : 1);
    if (productModalOptionsScroll) {
        productModalOptionsScroll.scrollTop = 0;
    }

    const optionNodes = Array.from(card.querySelectorAll("[data-product-options-source] [data-option-id]"));
    const companyNodes = Array.from(card.querySelectorAll("[data-product-companies-source] [data-company-id]"));
    const companyOptionCount = companyNodes.reduce(
        (total, companyNode) => total + companyNode.querySelectorAll("[data-company-option-id]").length,
        0,
    );
    const hasOptions = !isCompanyGrouped && optionNodes.length > 0;
    const hasCompanyGroups = isCompanyGrouped && companyOptionCount > 0;
    const hasSelections = hasOptions || hasCompanyGroups;
    const hasManyOptions = hasOptions ? optionNodes.length > 3 : companyOptionCount > 4 || companyNodes.length > 2;
    const requiresLogin = Boolean(productModalLoginPanel && productModalForm.hidden);
    productModalDialog?.classList.toggle("has-options", hasSelections);
    productModalDialog?.classList.toggle("has-no-options", !hasSelections);
    productModalDialog?.classList.toggle("has-few-options", hasSelections && !hasManyOptions);
    productModalDialog?.classList.toggle("has-many-options", hasSelections && hasManyOptions);
    productModalDialog?.classList.toggle("has-company-groups", hasCompanyGroups);
    productModalDialog?.classList.toggle("requires-login", requiresLogin);
    if (productModalOptionsScroll) {
        productModalOptionsScroll.hidden = !hasSelections || requiresLogin;
        productModalOptionsScroll.classList.toggle("has-many-options", hasSelections && hasManyOptions);
    }

    if (productModalOptions && productModalSubmit) {
        productModalOptions.querySelectorAll(".product-option-card").forEach((option) => option.remove());
        productModalOptions.hidden = !hasOptions;
        productModalSubmit.disabled = hasSelections;

        if (hasOptions) optionNodes.forEach((optionNode) => {
            const label = document.createElement("label");
            label.className = "product-option-card";

            const input = document.createElement("input");
            input.type = "radio";
            input.name = "option_id";
            input.value = optionNode.dataset.optionId || "";
            input.required = true;
            input.dataset.optionPrice = optionNode.dataset.optionPrice || "";
            input.dataset.optionUnitPrice = optionNode.dataset.optionUnitPrice || "";
            input.disabled = optionNode.dataset.optionAvailable === "false";

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
            if (input.disabled) {
                const unavailable = document.createElement("em");
                unavailable.textContent = document.documentElement.lang === "ar" ? "غير متوفر حالياً" : "Unavailable now";
                copy.append(unavailable);
                label.classList.add("is-unavailable");
            }

            input.addEventListener("change", () => {
                productModalUnitPriceText = input.dataset.optionPrice || price;
                productModalPrice.textContent = productModalUnitPriceText;
                syncProductModalSubmitState();
                syncProductModalTotal();
            });

            label.append(input, mark, copy);
            productModalOptions.append(label);
        });
    }

    if (productModalCompanies && productModalSubmit) {
        productModalCompanies.querySelectorAll(".product-company-card").forEach((company) => company.remove());
        productModalCompanies.hidden = !hasCompanyGroups;
        companyNodes.forEach((companyNode) => {
            productModalCompanies.append(buildProductCompanyCard(companyNode, price));
        });
    }
    syncProductModalSubmitState();

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
            productModalImage.onerror = () => {
                closeProductPhotoViewer();
                productModalImage.removeAttribute("src");
                productModalImage.removeAttribute("srcset");
                productModalImage.alt = "";
                productModalImage.hidden = true;
                if (productModalImageButton) {
                    productModalImageButton.hidden = true;
                    productModalImageButton.removeAttribute("aria-label");
                }
                productModalPlaceholder.hidden = false;
                productModalPlaceholder.textContent = title.slice(0, 1);
            };
            productModalImage.src = image;
            productModalImage.alt = title;
            productModalImage.hidden = false;
            if (productModalImageButton) {
                const viewImageLabel = document.documentElement.lang === "ar" ? `عرض صورة ${title} بالحجم الكامل` : `View ${title} full size`;
                productModalImageButton.setAttribute("aria-label", viewImageLabel);
                productModalImageButton.hidden = false;
            }
            productModalPlaceholder.hidden = true;
        } else {
            productModalImage.removeAttribute("src");
            productModalImage.removeAttribute("srcset");
            productModalImage.alt = "";
            productModalImage.hidden = true;
            if (productModalImageButton) {
                productModalImageButton.hidden = true;
                productModalImageButton.removeAttribute("aria-label");
            }
            productModalPlaceholder.hidden = false;
            productModalPlaceholder.textContent = title.slice(0, 1);
        }
    }

    const wasOpen = !productModal.hidden;
    productModal.hidden = false;
    if (!wasOpen) {
        window.history.pushState(
            {
                ...(window.history.state || {}),
                [PRODUCT_MODAL_HISTORY_KEY]: true,
            },
            "",
            window.location.href,
        );
    }
    syncProductModalTotal();
    syncModalOpenState();
};

const hideProductModal = () => {
    if (!productModal) {
        return;
    }

    closeProductPhotoViewer();
    productModal.hidden = true;
    syncModalOpenState();
};

const closeProductModal = (event) => {
    event?.preventDefault();
    event?.stopPropagation();

    if (!productModal || productModal.hidden) {
        return;
    }

    hideProductModal();
    if (window.history.state?.[PRODUCT_MODAL_HISTORY_KEY]) {
        window.history.back();
    }
};

const closeModals = () => {
    closeOfferModal();
    closeProductModal();
    setExcelModalOpen(false);
    setCartNoteModalOpen(false);
    setCheckoutConfirmModalOpen(false);
    closeOrderModals();
    closeCheckoutAddressModals();
};

const enhanceCartForm = (form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        event.stopPropagation();

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

            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.message || `Cart request failed with status ${response.status}`);
            }

            if (!payload.ok) {
                throw new Error(payload.message || "Cart update returned an unexpected payload.");
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
            if (!productModal?.contains(form) && !offerModal?.contains(form)) {
                form.submit();
            } else if (error?.message) {
                showCartToast(error.message);
            }
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
};

const updateCartPageTotals = (payload) => {
    if (!payload) {
        return;
    }

    const total = payload.has_weight_items ? payload.cart_total_range : payload.cart_total;
    document.querySelectorAll("[data-cart-summary-total], [data-cart-summary-subtotal]").forEach((element) => {
        element.textContent = total;
    });

    if (floatingCartCount && typeof payload.cart_count !== "undefined") {
        floatingCartCount.textContent = payload.cart_count;
        floatingCart?.classList.toggle("is-empty", payload.cart_count <= 0);
    }
    if (floatingCartTotal && total) {
        floatingCartTotal.textContent = total;
    }
};

const submitCartItemForm = async (form, card) => {
    if (!form || !card) {
        return;
    }

    card.classList.add("is-updating");
    try {
        const response = await window.fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: {
                Accept: "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (!response.ok) {
            form.submit();
            return;
        }

        const payload = await response.json();
        if (!payload.ok) {
            form.submit();
            return;
        }

        updateCartPageTotals(payload);

        if (payload.is_empty) {
            window.location.reload();
            return;
        }

        if (!payload.item) {
            card.classList.add("is-removing");
            window.setTimeout(() => {
                card.remove();
                if (!payload.has_unavailable_items) {
                    window.location.reload();
                }
            }, 190);
            return;
        }

        const quantityInput = form.querySelector("[data-cart-quantity-input]");
        const quantityLabel = card.querySelector("[data-cart-quantity-label]");
        const itemTotal = card.querySelector("[data-cart-item-total]");
        if (quantityInput) {
            quantityInput.value = payload.item.quantity;
            setQuantityValue(quantityInput, payload.item.quantity);
        }
        if (quantityLabel) {
            quantityLabel.textContent = payload.item.display_quantity;
        }
        if (itemTotal) {
            itemTotal.textContent = payload.item.is_weight_based
                ? payload.item.line_total_range
                : payload.item.line_total;
        }

        card.classList.remove("is-pulse");
        void card.offsetWidth;
        card.classList.add("is-pulse");
    } catch (error) {
        form.submit();
    } finally {
        card.classList.remove("is-updating");
    }
};

const enhanceCartQuantityForm = (form) => {
    const card = form.closest("[data-cart-item]");
    const input = form.querySelector("[data-cart-quantity-input]");
    const decreaseButton = form.querySelector("[data-cart-quantity-decrease]");
    const increaseButton = form.querySelector("[data-cart-quantity-increase]");
    let changeTimer = null;

    if (!card || !input) {
        return;
    }

    const setQuantity = (nextValue) => {
        setQuantityValue(input, nextValue);
        submitCartItemForm(form, card);
    };

    const step = Number(input.step || 1);
    decreaseButton?.addEventListener("click", () => setQuantity(getQuantityValue(input) - step));
    increaseButton?.addEventListener("click", () => setQuantity(getQuantityValue(input) + step));
    input.addEventListener("change", () => setQuantity(input.value));
    input.addEventListener("input", () => {
        window.clearTimeout(changeTimer);
        changeTimer = window.setTimeout(() => setQuantity(input.value), 550);
    });
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        submitCartItemForm(form, card);
    });
    setQuantityValue(input, input.value);
};

const enhanceCartRemoveForm = (form) => {
    const card = form.closest("[data-cart-item]");
    if (!card) {
        return;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        submitCartItemForm(form, card);
    });
};

const updateCartNoteCard = (card, note) => {
    if (!card) {
        return;
    }

    const cleanNote = String(note || "").trim();
    const hasNote = Boolean(cleanNote);
    const preview = card.querySelector("[data-cart-note-preview]");
    const previewText = card.querySelector("[data-cart-note-preview-text]");
    const opener = card.querySelector("[data-cart-note-open]");
    const deleteButton = card.querySelector("[data-cart-note-delete]");

    if (preview) {
        preview.hidden = !hasNote;
        preview.classList.toggle("is-empty", !hasNote);
    }
    if (previewText) {
        previewText.textContent = cleanNote;
    }
    if (opener) {
        opener.dataset.noteText = cleanNote;
        opener.textContent = hasNote
            ? (opener.dataset.editLabel || opener.textContent)
            : (opener.dataset.addLabel || opener.textContent);
    }
    if (deleteButton) {
        deleteButton.classList.toggle("is-hidden", !hasNote);
    }
};

const submitCartNote = async ({ action, note, card, submitButton }) => {
    if (!cartNoteModalForm || !action) {
        return;
    }

    const formData = new FormData(cartNoteModalForm);
    formData.set("note", note);

    try {
        if (submitButton) {
            submitButton.disabled = true;
        }

        const response = await window.fetch(action, {
            method: "POST",
            body: formData,
            headers: {
                Accept: "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        const payload = await response.json();

        if (!response.ok || !payload.ok) {
            throw new Error(payload.message || `Cart note request failed with status ${response.status}`);
        }

        updateCartNoteCard(card, payload.note || note);
        showCartToast(payload.message || "");
        setCartNoteModalOpen(false);
    } catch (error) {
        if (error?.message) {
            showCartToast(error.message);
        }
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
};

const openCartNoteModal = (button) => {
    if (!cartNoteModalForm || !cartNoteModalInput) {
        return;
    }

    activeCartNoteCard = button.closest("[data-cart-item]");
    cartNoteModalForm.action = button.dataset.noteAction || "";
    cartNoteModalInput.value = button.dataset.noteText || "";
    if (cartNoteModalTitle) {
        cartNoteModalTitle.textContent = button.dataset.noteTitle || cartNoteModalTitle.textContent;
    }
    setCartNoteModalOpen(true);
    cartNoteModalInput.focus();
};

const enhanceCartNoteForm = (form) => {
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        event.stopPropagation();
        submitCartNote({
            action: form.action,
            note: cartNoteModalInput?.value || "",
            card: activeCartNoteCard,
            submitButton: event.submitter || form.querySelector('button[type="submit"]'),
        });
    });
};

const getSelectedCheckoutService = () =>
    checkoutServiceOptions.find((input) => input.checked)?.value || "pickup";

const syncCheckoutTotals = () => {
    if (!checkoutFlow) {
        return;
    }

    const isDelivery = getSelectedCheckoutService() === "delivery";
    if (checkoutAddressPanel) {
        checkoutAddressPanel.hidden = !isDelivery;
    }

    if (!isDelivery) {
        if (checkoutDeliveryFee) {
            checkoutDeliveryFee.textContent = checkoutFlow.dataset.pickupFee || "0";
        }
        if (checkoutGrandTotal) {
            checkoutGrandTotal.textContent = checkoutFlow.dataset.pickupTotal || "";
        }
        return;
    }

    const selectedAddress = document.querySelector("[data-checkout-address-option]")?.selectedOptions?.[0];
    if (checkoutDeliveryFee && selectedAddress?.dataset.deliveryFeeDisplay) {
        checkoutDeliveryFee.textContent = selectedAddress.dataset.deliveryFeeDisplay;
    }
    if (checkoutGrandTotal && selectedAddress?.dataset.grandTotalDisplay) {
        checkoutGrandTotal.textContent = selectedAddress.dataset.grandTotalDisplay;
    }
};

const setCheckoutSubmitting = (isSubmitting) => {
    if (checkoutConfirmSubmit) {
        checkoutConfirmSubmit.disabled = isSubmitting;
        checkoutConfirmSubmit.classList.toggle("is-loading", isSubmitting);
    }
    if (checkoutConfirmApprove) {
        checkoutConfirmApprove.disabled = isSubmitting;
        checkoutConfirmApprove.classList.toggle("is-loading", isSubmitting);
    }
};

const replaceCheckoutHistoryEntry = () => {
    if (!checkoutConfirmForm || checkoutConfirmForm.dataset.historyReplaced === "true") {
        return;
    }

    const returnUrl = checkoutConfirmForm.dataset.checkoutReturnUrl;
    if (!returnUrl) {
        return;
    }

    window.history.replaceState(
        {
            ...(window.history.state || {}),
            checkoutSubmitted: true,
        },
        "",
        returnUrl,
    );
    checkoutConfirmForm.dataset.historyReplaced = "true";
};

const resetCheckoutConfirmationState = () => {
    if (!checkoutConfirmForm) {
        return;
    }

    delete checkoutConfirmForm.dataset.confirmed;
    delete checkoutConfirmForm.dataset.submitting;
    delete checkoutConfirmForm.dataset.historyReplaced;
    setCheckoutSubmitting(false);
    setCheckoutConfirmModalOpen(false);
};

const handleRestoredCheckoutPage = () => {
    if (!checkoutConfirmForm) {
        return;
    }

    const returnUrl = checkoutConfirmForm.dataset.checkoutReturnUrl;
    if (window.history.state?.checkoutSubmitted && returnUrl) {
        window.location.replace(returnUrl);
        return;
    }

    resetCheckoutConfirmationState();
};

const getFieldLabel = (field) => {
    const wrapper = field.closest("[data-field-wrapper], label");
    return wrapper?.querySelector(".field-label, span")?.textContent?.trim() || field.name || "Field";
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
    return Array.from(registerForm.querySelectorAll("[data-register-name-part]"))
        .filter((nameInput) => {
            const name = String(nameInput.value || "").trim();
            return name && !isArabicNameValue(name);
        })
        .map((field) => ({ field, message: messages.nameArabicOnly }));
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
            const field = list.closest("[data-field-wrapper], label")?.querySelector("input, select, textarea");
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
    const nameInputs = Array.from(registerForm.querySelectorAll("[data-register-name-part]"));
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
        if (!nameInputs.length || !isArabicLanguage()) {
            return;
        }

        nameInputs.forEach((nameInput) => {
            const name = String(nameInput.value || "").trim();
            setFieldValidationState(nameInput, name ? (isArabicNameValue(name) ? "valid" : "invalid") : null);
        });
    };

    const showLiveNameError = debounce(() => {
        if (!nameInputs.length || !isArabicLanguage()) {
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
    nameInputs.forEach((nameInput) => {
        nameInput.addEventListener("input", () => {
            updateNameValidationState();
            showLiveNameError();
        });
        nameInput.addEventListener("blur", () => {
            updateNameValidationState();
            const errors = collectRegisterNameErrors();
            if (errors.length) {
                showRegisterError(errors[0]);
                lastLiveNameErrorMessage = errors[0].message;
            }
        });
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

syncViewportHeightVariable();
window.visualViewport?.addEventListener("resize", syncViewportHeightVariable);
window.visualViewport?.addEventListener("scroll", syncViewportHeightVariable);
window.addEventListener("resize", syncViewportHeightVariable);

if (registerForm) {
    if ("scrollRestoration" in window.history) {
        window.history.scrollRestoration = "manual";
    }
    const resetRegisterScrollPosition = () => {
        window.requestAnimationFrame(() => window.scrollTo(0, 0));
    };
    resetRegisterScrollPosition();
    window.addEventListener("pageshow", resetRegisterScrollPosition);
}

passwordVisibilityToggles.forEach(enhancePasswordVisibilityToggle);
syrianPhoneInputs.forEach(enhanceSyrianPhoneInput);
syrianPhoneControls.forEach(enhanceSyrianPhoneControl);
deliveryAreaGroups.forEach(enhanceDeliveryAreaGroup);
dashboardSubAreaFormsets.forEach(enhanceDashboardSubAreaFormset);
dashboardDeliveryAreaForms.forEach(enhanceDashboardDeliveryAreaForm);
dashboardProductOptionPanels.forEach(enhanceDashboardProductOptionsPanel);
dashboardCompanyFormsets.forEach(enhanceDashboardCompanyFormset);
expectedTimePresetButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const form = button.closest("form");
        const input = form?.querySelector('input[name="expected_time_minutes"]');
        if (input) {
            input.value = button.dataset.timePreset || "";
            input.focus();
        }
    });
});

document.addEventListener("click", (event) => {
    syrianPhoneControls.forEach((control) => {
        if (!control.contains(event.target)) {
            closeSyrianPhoneMenu(control);
        }
    });

    if (
        siteHeader?.classList.contains("is-mobile-nav-open") &&
        !mobileNavMenu?.contains(event.target) &&
        !mobileNavToggle?.contains(event.target)
    ) {
        setMobileNavOpen(false);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }

    syrianPhoneControls.forEach(closeSyrianPhoneMenu);
    setMobileNavOpen(false);
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

productModalImageButton?.addEventListener("click", openProductPhotoViewer);
productPhotoViewer?.querySelectorAll("[data-product-photo-viewer-close]").forEach((element) => {
    element.addEventListener("click", closeProductPhotoViewer);
});

enhanceBusyCountdowns();
enhanceDashboardCenterCountdown();
enhanceNewOrderAlerts();
activeOrderStatusRegions.forEach(enhanceActiveOrderStatusRegion);
categoryProductSearches.forEach(enhanceCategoryProductSearch);
homeShelfRows.forEach(enhanceHomeShelfRow);

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
        event.stopPropagation();
        openProductModal(card);
    });
});

quantityControls.forEach((control) => {
    const input = control.querySelector('input[name="quantity"]');
    const decreaseButton = control.querySelector("[data-quantity-decrease]");
    const increaseButton = control.querySelector("[data-quantity-increase]");

    decreaseButton?.addEventListener("click", () => {
        setQuantityValue(input, getQuantityValue(input) - Number(input?.step || 1));
        if (productModalForm?.contains(input)) {
            syncProductModalTotal();
        }
    });

    increaseButton?.addEventListener("click", () => {
        setQuantityValue(input, getQuantityValue(input) + Number(input?.step || 1));
        if (productModalForm?.contains(input)) {
            syncProductModalTotal();
        }
    });

    input?.addEventListener("change", () => {
        setQuantityValue(input, getQuantityValue(input));
        if (productModalForm?.contains(input)) {
            syncProductModalTotal();
        }
    });

    input?.addEventListener("input", () => {
        if (productModalForm?.contains(input)) {
            syncProductModalTotal();
        }
    });
    setQuantityValue(input, input?.value);
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

dashboardColumnFilters.forEach((filter) => {
    filter.addEventListener("toggle", () => {
        if (!filter.open) {
            return;
        }
        dashboardColumnFilters.forEach((otherFilter) => {
            if (otherFilter !== filter) {
                otherFilter.open = false;
            }
        });
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        if (productPhotoViewer && !productPhotoViewer.hidden) {
            closeProductPhotoViewer();
            return;
        }
        closeModals();
        setDashboardDrawerOpen(false);
        setMobileNavOpen(false);
    }
});

mobileNavToggle?.addEventListener("click", () => {
    const isOpen = mobileNavToggle.getAttribute("aria-expanded") === "true";
    setMobileNavOpen(!isOpen);
});

mobileNavMenu?.querySelectorAll("a, button").forEach((item) => {
    item.addEventListener("click", () => setMobileNavOpen(false));
});

mobileNavMediaQuery.addEventListener("change", () => {
    if (!mobileNavMediaQuery.matches) {
        setMobileNavOpen(false);
        mobileNavMenu?.removeAttribute("aria-hidden");
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
dashboardProductTypeInput?.addEventListener("change", syncDashboardProductOptionsPanel);
syncDashboardProductOptionsPanel();

excelModalOpen?.addEventListener("click", () => setExcelModalOpen(true));
excelModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => setExcelModalOpen(false));
});
cartNoteOpeners.forEach((button) => {
    button.addEventListener("click", () => openCartNoteModal(button));
});
cartNoteDeleteButtons.forEach((button) => {
    button.addEventListener("click", () => {
        submitCartNote({
            action: button.dataset.noteAction || "",
            note: "",
            card: button.closest("[data-cart-item]"),
            submitButton: button,
        });
    });
});
cartNoteModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => setCartNoteModalOpen(false));
});
orderModalOpeners.forEach((opener) => {
    opener.addEventListener("click", () => {
        const targetSelector = opener.dataset.orderModalTarget;
        const targetModal = targetSelector ? document.querySelector(targetSelector) : null;
        setOrderModalOpen(true, targetModal);
    });
});
orderModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => {
        setOrderModalOpen(false, closer.closest("[data-order-modal]"));
    });
});
checkoutAddressModalOpeners.forEach((opener) => {
    opener.addEventListener("click", () => {
        const targetSelector = opener.dataset.checkoutAddressModalTarget;
        const targetModal = targetSelector ? document.querySelector(targetSelector) : checkoutAddressModals[0];
        setCheckoutAddressModalOpen(true, targetModal);
    });
});
checkoutAddressModalClosers.forEach((closer) => {
    closer.addEventListener("click", () => {
        setCheckoutAddressModalOpen(false, closer.closest("[data-checkout-address-modal]"));
    });
});
checkoutAddressOptions.forEach((input) => {
    if (input.tagName === "SELECT") {
        input.dataset.previousAddressValue = input.value;
    }

    const handleCheckoutAddressChange = () => {
        const selectedOption = input.tagName === "SELECT" ? input.selectedOptions?.[0] : input;
        if (input.tagName === "SELECT" && input.value === "__add_new__") {
            const fallbackOption = Array.from(input.options).find((option) => option.value !== "__add_new__");
            input.value = input.dataset.previousAddressValue || fallbackOption?.value || "";
            if (input.value && !input.dataset.previousAddressValue) {
                input.dataset.previousAddressValue = input.value;
            }
            setCheckoutAddressModalOpen(true);
            return;
        }
        if (input.tagName === "SELECT") {
            input.dataset.previousAddressValue = input.value;
        }
        syncCheckoutTotals();
    };

    input.addEventListener("input", handleCheckoutAddressChange);
    input.addEventListener("change", handleCheckoutAddressChange);
});
checkoutServiceOptions.forEach((input) => {
    input.addEventListener("change", syncCheckoutTotals);
});
syncCheckoutTotals();
checkoutConfirmClosers.forEach((closer) => {
    closer.addEventListener("click", () => setCheckoutConfirmModalOpen(false));
});
checkoutConfirmForm?.addEventListener("submit", (event) => {
    if (checkoutConfirmForm.dataset.confirmed === "true") {
        if (checkoutConfirmForm.dataset.submitting === "true") {
            event.preventDefault();
            return;
        }
        checkoutConfirmForm.dataset.submitting = "true";
        setCheckoutConfirmModalOpen(false);
        replaceCheckoutHistoryEntry();
        setCheckoutSubmitting(true);
        return;
    }

    event.preventDefault();
    setCheckoutConfirmModalOpen(true);
});
checkoutConfirmApprove?.addEventListener("click", () => {
    if (!checkoutConfirmForm || checkoutConfirmApprove.disabled) {
        return;
    }

    checkoutConfirmForm.dataset.confirmed = "true";
    checkoutConfirmForm.requestSubmit();
});
window.addEventListener("pageshow", handleRestoredCheckoutPage);
syncModalOpenState();

window.addEventListener("popstate", () => {
    if (productModal && !productModal.hidden) {
        hideProductModal();
    }
});

confirmationForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (!window.confirm(form.dataset.confirmSubmit || "")) {
            event.preventDefault();
        }
    });
});

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
cartQuantityForms.forEach(enhanceCartQuantityForm);
cartRemoveForms.forEach(enhanceCartRemoveForm);
cartNoteForms.forEach(enhanceCartNoteForm);
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
