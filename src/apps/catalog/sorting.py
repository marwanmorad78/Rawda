import unicodedata


ARABIC_LETTER_ORDER = {
    letter: index
    for index, letter in enumerate(
        (
            "\u0627",
            "\u0628",
            "\u062a",
            "\u062b",
            "\u062c",
            "\u062d",
            "\u062e",
            "\u062f",
            "\u0630",
            "\u0631",
            "\u0632",
            "\u0633",
            "\u0634",
            "\u0635",
            "\u0636",
            "\u0637",
            "\u0638",
            "\u0639",
            "\u063a",
            "\u0641",
            "\u0642",
            "\u0643",
            "\u0644",
            "\u0645",
            "\u0646",
            "\u0647",
            "\u0648",
            "\u064a",
        )
    )
}

ARABIC_NORMALIZATION_TRANSLATION = str.maketrans(
    {
        "\u0623": "\u0627",
        "\u0625": "\u0627",
        "\u0622": "\u0627",
        "\u0649": "\u064a",
        "\u0629": "\u0647",
        "\u0640": "",
    }
)


def normalize_arabic_sort_text(value):
    normalized = unicodedata.normalize("NFKD", (value or "").lstrip())
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )
    return normalized.translate(ARABIC_NORMALIZATION_TRANSLATION)


def arabic_sort_key(value):
    normalized = normalize_arabic_sort_text(value)
    return tuple(
        (0, ARABIC_LETTER_ORDER[character])
        if character in ARABIC_LETTER_ORDER
        else (1, character.casefold())
        for character in normalized
    )


def product_arabic_sort_name(product):
    return getattr(product, "name_ar", "") or getattr(product, "name", "")


def product_display_order(product):
    return getattr(product, "display_order", 0)


def sort_category_products(products):
    return sorted(
        products,
        key=lambda product: (
            product_display_order(product),
            arabic_sort_key(product_arabic_sort_name(product)),
            getattr(product, "pk", 0) or 0,
        ),
    )
