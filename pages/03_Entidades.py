from dashboard_parquets import configure_page, get_dashboard_context, render_entities, render_shared_frame


def main() -> None:
    configure_page("Entidades | Dashboard Parquets OSC")
    context = get_dashboard_context()
    if context is None:
        return
    if not render_shared_frame(context, current_page="entidades"):
        return
    render_entities(context.filtered)


if __name__ == "__main__":
    main()
