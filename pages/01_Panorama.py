from dashboard_parquets import configure_page, get_dashboard_context, render_overview, render_shared_frame


def main() -> None:
    configure_page("Panorama | Dashboard Parquets OSC")
    context = get_dashboard_context()
    if context is None:
        return
    if not render_shared_frame(context, current_page="panorama"):
        return
    render_overview(context.filtered, context.data, context.filtered_without_year)


if __name__ == "__main__":
    main()
