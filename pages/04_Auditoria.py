from dashboard_parquets import configure_page, get_dashboard_context, render_audit, render_shared_frame


def main() -> None:
    configure_page("Auditoria | Dashboard Parquets OSC")
    context = get_dashboard_context()
    if context is None:
        return
    if not render_shared_frame(context, current_page="auditoria"):
        return
    render_audit(context.filtered, context.data, context.files_df)


if __name__ == "__main__":
    main()
