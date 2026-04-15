from dashboard_parquets import configure_page, get_dashboard_context, render_shared_frame, render_territory


def main() -> None:
    configure_page("Territorio | Dashboard Parquets OSC")
    context = get_dashboard_context()
    if context is None:
        return
    if not render_shared_frame(context, current_page="territorio"):
        return
    render_territory(context.filtered)


if __name__ == "__main__":
    main()
