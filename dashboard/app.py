
import streamlit as st
import streamlit.components.v1 as components
from dashboard.api_client import (
    get_experiments,
    get_experiment,
    get_experiment_metrics,
    get_experiment_health,
    get_experiment_decision,
    get_experiment_statistics,
    create_experiment,
    update_experiment_status,
    APIClientError,
)
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ExperimentGuard | Experiment Analytics",
    page_icon="EG",
    layout="wide",
    initial_sidebar_state="expanded",
)



def render_login_visual():
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            * { box-sizing: border-box; }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: transparent;
                color: #182033;
            }

            .visual {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 18px;
                padding: 25px;
                overflow: hidden;
            }

            .eyebrow {
                color: #4659db;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
            }

            h2 {
                font-family: Georgia, serif;
                font-size: 26px;
                font-weight: 400;
                margin: 12px 0;
            }

            .description {
                font-size: 13px;
                line-height: 1.7;
                color: #64748b;
            }

            .chart {
                margin-top: 25px;
                padding: 18px;
                background: #f8f9fd;
                border: 1px solid #e8eaf4;
                border-radius: 14px;
            }

            .chart-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            .live {
                color: #21865d;
                background: #e5f5ed;
                padding: 6px 9px;
                border-radius: 20px;
            }

            svg {
                width: 100%;
                height: 190px;
                margin-top: 14px;
            }

            .line-a {
                fill: none;
                stroke: #a5adbd;
                stroke-width: 3;
                stroke-linecap: round;
                stroke-dasharray: 500;
                stroke-dashoffset: 500;
                animation: draw-loop 8s ease-in-out infinite;
            }

            .line-b {
                fill: none;
                stroke: #4659db;
                stroke-width: 3;
                stroke-linecap: round;
                stroke-dasharray: 500;
                stroke-dashoffset: 500;
                animation: draw-loop 8s ease-in-out 0.5s infinite;
            }

            @keyframes draw {
                to { stroke-dashoffset: 0; }
            }

            .pulse {
                fill: #4659db;
                transform-origin: center;
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.35; }
            }


            @keyframes draw-loop {
                0%, 25% {
                    stroke-dashoffset: 500;
                }

                65%, 85% {
                    stroke-dashoffset: 0;
                }

                100% {
                    stroke-dashoffset: 500;
                }
            }


            .legend {
                display: flex;
                gap: 18px;
                margin-top: 8px;
                font-size: 11px;
                color: #64748b;
            }

            .dot {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 5px;
            }

            .features {
                display: flex;
                flex-direction: column;
                gap: 13px;
                margin-top: 24px;
                font-size: 12px;
                color: #475569;
            }

            .check {
                color: #21865d;
                margin-right: 9px;
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation: none !important;
                }
                .line-a, .line-b {
                    stroke-dashoffset: 0;
                }
            }
        </style>
        </head>
        <body>
            <div class="visual">
                <div class="eyebrow">THE EXPERIMENT LAB</div>

                <h2>Every experiment tells a story.</h2>

                <p class="description">
                    Measure impact. Understand uncertainty.
                    Make better rollout decisions.
                </p>

                <div class="chart">
                    <div class="chart-header">
                        <span>EXPERIMENT PREVIEW</span>
                        <span class="live">● ILLUSTRATIVE</span>
                    </div>

                    <svg viewBox="0 0 400 190"
                         role="img"
                         aria-label="Illustrative conversion trends for two experiment variants">

                        <g stroke="#e2e8f0"
                           stroke-dasharray="4 5">
                            <line x1="10" y1="40" x2="390" y2="40"/>
                            <line x1="10" y1="90" x2="390" y2="90"/>
                            <line x1="10" y1="140" x2="390" y2="140"/>
                        </g>

                        <path class="line-a"
                              d="M10 155 C60 148 90 145 130 135
                                 S220 120 270 105 S350 95 390 85"/>

                        <path class="line-b"
                              d="M10 155 C60 145 90 120 130 115
                                 S220 85 270 70 S350 40 390 22"/>

                        <circle class="pulse"
                                cx="390" cy="22" r="5"/>
                    </svg>

                    <div class="legend">
                        <span>
                            <i class="dot"
                               style="background:#a5adbd"></i>
                            Control A
                        </span>

                        <span>
                            <i class="dot"
                               style="background:#4659db"></i>
                            Variant B
                        </span>
                    </div>
                </div>

                <div class="features">
                    <div><span class="check">✓</span>
                        Controlled A/B experiments</div>
                    <div><span class="check">✓</span>
                        Statistical significance analysis</div>
                    <div><span class="check">✓</span>
                        Experiment health monitoring</div>
                    <div><span class="check">✓</span>
                        Evidence-based rollout recommendations</div>
                </div>
            </div>
        </body>
        </html>
        """,
        height=540,
        scrolling=False,
    )


from dashboard.api_client import (
    login_user,
    register_user,
    get_current_account,
)



if "access_token" not in st.session_state:
    st.session_state.access_token = None


if st.session_state.access_token is None:

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1200px;
            padding-top: 3rem;
        }

        div[data-testid="stForm"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 20px;
        }

        div[data-testid="stFormSubmitButton"] button {
            background: #4659db;
            color: white;
            border: none;
            border-radius: 8px;
            min-height: 43px;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background: #3446c5;
            color: white;
        }


        /* Animate the two login columns */
        .st-key-eg_login_left {
            opacity: 0;
            animation: eg-slide-left 0.9s ease 2.2s forwards;
        }

        .st-key-eg_login_right {
            opacity: 0;
            animation: eg-slide-right 0.9s ease 2.4s both;

        }

        @keyframes eg-slide-left {
            from {
                opacity: 0;
                transform: translateX(-24px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes eg-slide-right {
            from {
                opacity: 0;
                transform: translateX(24px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .st-key-eg_login_left,
            .st-key-eg_login_right {
                opacity: 1;
                animation: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="eg-brand">
            <div class="eg-brand-row">
                <span class="eg-brand-logo">EG</span>
                <span class="eg-typewriter">ExperimentGuard</span>
            </div>
            <div class="eg-brand-subtitle">
                EXPERIMENT INTELLIGENCE PLATFORM
            </div>
        </div>

        <style>
        .eg-brand {
            margin-bottom: 32px;
        }

        .eg-brand-row {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .eg-brand-logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            border-radius: 11px;
            background: #171923;
            color: white;
            font-family: Georgia, serif;
            font-size: 17px;
        }



            .eg-typewriter {
                display: inline-block;
                overflow: hidden;
                white-space: nowrap;
                width: 0;
                font-family: Georgia, serif;
                font-size: clamp(24px, 3vw, 39px);
                color: #141b2d;
                letter-spacing: -1px;
                animation: eg-type 8s steps(15, end) infinite;
            }

            @keyframes eg-type {
                0% {
                    width: 0;
                }
                30%, 70% {
                    width: 16ch;
                }
                100% {
                    width: 0;
                }
            }


        .eg-brand-subtitle {
            margin-top: 12px;
            color: #64748b;
            font-size: 11px;
            letter-spacing: 2px;
            opacity: 0;
            animation: eg-fade-up 0.8s ease 1.9s forwards;
        }


        @keyframes eg-type {
            0% {
                width: 0;
            }

            25% {
                width: 100%;
            }

            95% {
                width: 100%;
            }

            100% {
                width: 0;
            }
        }



        @keyframes eg-fade-up {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .eg-typewriter {
                width: auto;
                animation: eg-type 8s steps(15, end) infinite;
            }

            .eg-brand-subtitle {
                opacity: 1;
                animation: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    st.write("")

    left_col, right_col = st.columns(
    [1.15, 1],
    gap="large",
    vertical_alignment="center",
)

    with left_col:
        render_login_visual()

    with right_col:
        st.markdown("## Welcome to ExperimentGuard")
        st.caption(
            "Your workspace for experiments, insights, "
            "and confident decisions."
        )

        login_tab, register_tab = st.tabs(
            ["Sign In", "Create Account"]
        )

        with login_tab:
            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                )

                if submitted:
                    try:
                        result = login_user(email, password)

                        st.session_state.access_token = (
                            result["access_token"]
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "Unable to sign in. "
                            "Please check your credentials."
                        )

        with register_tab:
            with st.form("register_form"):
                email = st.text_input(
                    "Email address",
                    key="register_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                    help="Use at least 12 characters.",
                )

                submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                )

                if submitted:
                    try:
                        register_user(email, password)

                        st.success(
                            "Account created successfully. "
                            "Please switch to Sign In."
                        )

                    except Exception:
                        st.error(
                            "Unable to create account. "
                            "Check your details or try another email."
                        )

    st.stop()


try:
    account = get_current_account(st.session_state.access_token)
except Exception:
    st.session_state.access_token = None
    st.warning("Your session expired. Please sign in again.")
    st.stop()



# --------------------------------------------------
# PROFESSIONAL LIGHT THEME
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main application */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Compact sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        min-width: 76px !important;
        max-width: 76px !important;
        width: 76px !important;
    }

    [data-testid="stSidebar"] .stVerticalBlock {
        gap: 0.65rem;
    }

    [data-testid="stSidebar"] .block-container {
        padding-left: 10px;
        padding-right: 10px;
        padding-top: 1.5rem;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 9px;
        justify-content: center;
        padding: 8px;
        box-shadow: none;
        border: none;
    }

    /* Selected navigation item */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #EFF6FF;
        color: #2563EB;
    }

    /* Unselected navigation item */
    [data-testid="stSidebar"] .stButton > button[kind="tertiary"] {
        background-color: transparent;
        color: #64748B;
    }

    /* Hover state */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F1F5F9;
        color: #2563EB;
    }

    /* Typography */
    h1, h2, h3 {
        color: #0F172A;
        letter-spacing: -0.025em;
    }

    /* Dashboard cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <style>
    /* Keep sidebar content arranged vertically */
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        min-height: 100%;
        display: flex;
        flex-direction: column;
    }

    /* Push the account menu to the bottom */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] {
        margin-top: auto;
        margin-bottom: 12px;
    }

    /* Remove the square button background and border */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 6px !important;
        min-height: 38px;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] button:hover {
        background: rgba(100, 116, 139, 0.10) !important;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# NAVIGATION CONFIGURATION
# --------------------------------------------------

PAGES = {
    "Overview": ":material/home:",
    "Experiments": ":material/science:",
    "Results": ":material/monitoring:",
    "Health": ":material/health_and_safety:",
    "Decisions": ":material/fact_check:",
}

if "page" not in st.session_state:
    st.session_state.page = "Overview"


# --------------------------------------------------
# COMPACT ICON SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        "<div style='text-align:center; "
        "font-weight:800; font-size:18px; "
        "color:#2563EB;'>EG</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    for page_name, icon in PAGES.items():

        if st.button(
            "",
            icon=icon,
            help=page_name,
            key=f"nav_{page_name}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "tertiary"
            ),
        ):
            st.session_state.page = page_name
            st.rerun()

    st.divider()
    st.caption("v1.0")


with st.sidebar:
    st.markdown(
        '<div class="account-menu-anchor"></div>',
        unsafe_allow_html=True,
    )

    with st.popover(
        "👤",
        help="My Account",
        use_container_width=True,
    ):
        st.markdown("### My Account")
        st.caption(account["email"])

        st.divider()

        st.markdown("**Account settings**")
        st.caption("Profile and security settings coming soon.")

        if st.button(
            "Log out",
            key="account_logout",
            use_container_width=True,
        ):
            st.session_state.access_token = None
            st.rerun()

        st.divider()
        st.caption("DANGER ZONE")

        if st.button(
            "Delete account",
            key="account_delete",
            use_container_width=True,
        ):
            st.session_state.show_delete_confirmation = True




if st.session_state.get("show_delete_confirmation", False):
    st.warning(
        "Account deletion is not available yet. "
        "We will implement password verification and "
        "a secure deletion endpoint before enabling it."
    )

    if st.button("Cancel", key="cancel_delete_account"):
        st.session_state.show_delete_confirmation = False
        st.rerun()



# --------------------------------------------------
# CURRENT PAGE
# --------------------------------------------------

page = st.session_state.page


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":


    # Fetch real experiments from FastAPI
    try:
        experiments = get_experiments(token=st.session_state.access_token)
        api_error = None
    except APIClientError as exc:
        experiments = []
        api_error = str(exc)

    total_experiments = len(experiments)

    running_experiments = sum(
        1
        for experiment in experiments
        if experiment["status"] == "running"
    )


    st.caption("WORKSPACE / OVERVIEW")

    if api_error:
        st.error(f"Unable to load experiments: {api_error}")

    st.title("Experiment Overview")

    st.write(
        "Monitor experiment performance, evaluate statistical "
        "evidence, and make data-driven rollout decisions."
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.caption("Total Experiments")
            st.subheader(str(total_experiments))

    with col2:
        with st.container(border=True):
            st.caption("Running Experiments")
            st.subheader(str(running_experiments))

    with col3:
        with st.container(border=True):
            st.caption("Healthy Experiments")
            st.subheader("—")

    with col4:
        with st.container(border=True):
            st.caption("Ready for Decision")
            st.subheader("—")

    st.write("")


    with st.container(border=True):
        st.subheader("Recent Experiments")

        if experiments:
            experiment_rows = []

            for experiment in experiments:
                experiment_rows.append(
                    {
                        "Experiment": experiment["name"],
                        "Experiment ID": experiment["experiment_id"],
                        "Status": experiment["status"].title(),
                        "Primary Metric": experiment["primary_metric"],
                        "Traffic Split": " / ".join(
                            f"{variant}: {weight:.0%}"
                            for variant, weight in experiment["variants"].items()
                        ),
                    }
                )

            st.dataframe(
                experiment_rows,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.caption("No experiments available.")


    st.write("")

    with st.container(border=True):

        st.subheader("Decision Activity")

        st.caption(
            "Rollout recommendations and health warnings "
            "will appear here."
        )


# --------------------------------------------------
# EXPERIMENTS PAGE
# --------------------------------------------------



# --------------------------------------------------
# EXPERIMENTS PAGE
# --------------------------------------------------

elif page == "Experiments":

    st.caption("WORKSPACE / EXPERIMENTS")


    if st.session_state.get("selected_experiment_id"):

        if st.button(
            "Back to Experiments",
            icon=":material/arrow_back:",
            type="tertiary",
        ):
            st.session_state.selected_experiment_id = None
            st.rerun()

        experiment_id = st.session_state.selected_experiment_id

        try:
            experiment = get_experiment(experiment_id)
        except APIClientError as exc:
            st.error(str(exc))
            st.stop()

        st.caption(f"EXPERIMENTS / {experiment_id}")
        st.title(experiment["name"])
        st.caption(
            f"Status: {experiment['status'].title()}"
        )

        setup_tab, diagnostics_tab, results_tab, summary_tab = st.tabs(
            ["Setup", "Diagnostics", "Results", "Summary"]
        )


        with setup_tab:
            st.subheader("Experiment Configuration")

            st.write(
                "**Experiment ID:**",
                experiment["experiment_id"],
            )
            st.write(
                "**Primary Metric:**",
                experiment["primary_metric"],
            )
            st.write(
                "**Status:**",
                experiment["status"].title(),
            )

            st.subheader("Experiment Planning")

            planned_sample_size = experiment.get("planned_sample_size")

            if planned_sample_size is not None:
                st.metric(
                    "Planned Sample Size",
                    f"{planned_sample_size:,} users",
                )
            else:
                st.info(
                    "No planned sample size was configured for this experiment."
                )

            st.subheader("Traffic Allocation")

            for variant, weight in experiment["variants"].items():
                st.write(f"Variant {variant}: {weight:.0%}")


            st.divider()
            st.subheader("Experiment Lifecycle")

            current_status = experiment["status"]

            if current_status == "draft":
                actions = [("Start Experiment", "running")]

            elif current_status == "running":
                actions = [
                    ("Pause Experiment", "paused"),
                    ("Complete Experiment", "completed"),
                ]

            elif current_status == "paused":
                actions = [
                    ("Resume Experiment", "running"),
                    ("Complete Experiment", "completed"),
                ]

            else:
                actions = []
                st.success(
                    "This experiment is completed. "
                    "No further status changes are allowed."
                )

            if actions:
                action_columns = st.columns(len(actions))

                for column, (label, new_status) in zip(
                    action_columns, actions
                ):
                    with column:
                        if st.button(
                            label,
                            key=f"{experiment_id}_{new_status}",
                            use_container_width=True,
                        ):
                            try:
                                update_experiment_status(
                                    experiment_id,
                                    new_status,
                                )
                            except APIClientError as exc:
                                st.error(str(exc))
                            else:
                                st.rerun()




        with diagnostics_tab:
            st.subheader("Experiment Diagnostics")
            st.caption(
                "Monitor assignment integrity, traffic allocation, "
                "and sample ratio mismatch."
            )

            try:
                health = get_experiment_health(experiment_id)

            except APIClientError as exc:
                st.error(str(exc))

            else:
                status = health["status"]
                validation = health["validation"]
                srm = health.get("srm")

                if srm is None:
                    srm = {
                        "has_srm": None,
                        "p_value": None,
                        "alpha": None,
                        "chi_square": None,
                        "total_users": 0,
                        "observed_counts": {},
                        "expected_weights": {},
                    }

                total_users = validation["total_users"]

                col1, col2 = st.columns(2)

                col1.metric(
                    "Assigned Users",
                    f"{total_users:,}",
                )

                col2.metric(
                    "Experiment Health",
                    status.replace("_", " ").title(),
                )


                st.markdown("#### Assignment Validation")

                if total_users == 0:
                    st.info(
                        "No users assigned yet. Diagnostics will "
                        "be available after data collection begins."
                    )

                elif validation["issues"]:
                    for issue in validation["issues"]:
                        st.warning(issue)

                else:
                    st.success(
                        "No assignment validation issues detected."
                    )

                if srm is not None:
                    st.markdown("#### Traffic Allocation")

                    observed = srm["observed_counts"]
                    weights = srm["expected_weights"]

                    variant_names = list(observed.keys())

                    expected_counts = [
                        total_users * weights[name]
                        for name in variant_names
                    ]

                    observed_counts = [
                        observed[name]
                        for name in variant_names
                    ]

                    import plotly.graph_objects as go

                    allocation_fig = go.Figure()

                    allocation_fig.add_trace(
                        go.Bar(
                            name="Expected",
                            x=variant_names,
                            y=expected_counts,
                            marker_color="#94A3B8",
                        )
                    )

                    allocation_fig.add_trace(
                        go.Bar(
                            name="Observed",
                            x=variant_names,
                            y=observed_counts,
                            marker_color="#2563EB",
                        )
                    )

                    allocation_fig.update_layout(
                        barmode="group",
                        height=340,
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        yaxis_title="Assigned Users",
                        font=dict(color="#334155"),
                        legend=dict(orientation="h", y=1.15),
                    )

                    allocation_fig.update_yaxes(
                        rangemode="tozero",
                        gridcolor="#E2E8F0",
                    )

                    st.plotly_chart(
                        allocation_fig,
                        width="stretch",
                    )

                    st.markdown("#### Sample Ratio Mismatch")

                    s1, s2, s3 = st.columns(3)

                    s1.metric(
                        "SRM P-value",
                        f"{srm['p_value']:.6f}",
                    )

                    s2.metric(
                        "SRM Threshold",
                        f"{srm['alpha']:.3f}",
                    )

                    s3.metric(
                        "Chi-square Statistic",
                        f"{srm['chi_square']:.3f}",
                    )

                    if srm["has_srm"]:
                        st.error(
                            "Sample ratio mismatch detected. "
                            "Investigate experiment assignment "
                            "before trusting the results."
                        )
                    else:
                        st.success(
                            "No sample ratio mismatch detected "
                            "at the configured threshold."
                        )

                    st.caption(
                        "SRM compares observed traffic allocation "
                        "against the expected variant distribution. "
                        "A low p-value may indicate assignment, "
                        "tracking, or data-quality problems."
                    )



        with results_tab:
            st.subheader("Experiment Results")
            st.caption(
                "Compare experiment variants, measure improvement, "
                "and evaluate statistical significance."
            )

            try:
                metrics = get_experiment_metrics(experiment_id)
                statistics_response = get_experiment_statistics(
                    experiment_id
                )

            except APIClientError as exc:
                st.error(str(exc))

            else:
                variants = metrics["variants"]
                total_users = sum(
                    item["assigned_users"]
                    for item in variants.values()
                )

                if total_users == 0:
                    st.info(
                        "No experiment data yet. Start the experiment "
                        "and record assignments and conversion events "
                        "to view results."
                    )

                else:
                    # 1. Summary metrics
                    st.markdown("#### Performance Overview")

                    a = variants["A"]
                    b = variants["B"]

                    lift = metrics["relative_lift_percent"]
                    absolute_lift = (
                        b["conversion_rate"] - a["conversion_rate"]
                    ) * 100

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric(
                        "Control A",
                        f"{a['conversion_rate']:.2%}",
                        f"{a['converted_users']:,} conversions",
                        delta_color="off",
                    )

                    col2.metric(
                        "Treatment B",
                        f"{b['conversion_rate']:.2%}",
                        f"{b['converted_users']:,} conversions",
                        delta_color="off",
                    )

                    col3.metric(
                        "Relative Lift",
                        f"{lift:+.2f}%" if lift is not None else "N/A",
                    )

                    col4.metric(
                        "Absolute Difference",
                        f"{absolute_lift:+.2f} pp",
                    )

                    # 2. Conversion rate chart
                    st.markdown("#### Conversion Rate Comparison")

                    import plotly.graph_objects as go

                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            x=["Control A", "Treatment B"],
                            y=[
                                a["conversion_rate"] * 100,
                                b["conversion_rate"] * 100,
                            ],
                            marker_color=["#94A3B8", "#2563EB"],
                            text=[
                                f"{a['conversion_rate']:.2%}",
                                f"{b['conversion_rate']:.2%}",
                            ],
                            textposition="outside",
                            hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
                        )
                    )

                    fig.update_layout(
                        height=340,
                        margin=dict(l=20, r=20, t=25, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        yaxis_title="Conversion Rate (%)",
                        showlegend=False,
                        font=dict(color="#334155"),
                    )

                    fig.update_yaxes(
                        rangemode="tozero",
                        gridcolor="#E2E8F0",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                    # 3. Statistical significance
                    st.markdown("#### Statistical Significance")

                    if statistics_response is None:
                        st.info(
                            "Statistical results require assigned users "
                            "in both variants."
                        )

                    else:
                        stats = statistics_response["statistics"]

                        p_value = stats["p_value"]
                        alpha = stats["alpha"]
                        significant = stats["is_significant"]

                        s1, s2, s3 = st.columns(3)

                        s1.metric("P-value", f"{p_value:.6f}")
                        s2.metric("Significance Level", f"{alpha:.2f}")
                        s3.metric(
                            "Z-statistic",
                            f"{stats['z_statistic']:.3f}",
                        )


                    if significant:
                        if stats["absolute_difference"] > 0:
                            st.success(
                                "Treatment B shows a statistically significant "
                                "improvement over Control A."
                            )
                        elif stats["absolute_difference"] < 0:
                            st.warning(
                                "Treatment B performs significantly worse "
                                "than Control A."
                            )
                        else:
                            st.info(
                                "A statistically significant difference was reported, "
                                "but the estimated difference is zero."
                            )
                    else:
                        st.info(
                            "The observed difference is not statistically "
                            "significant at the configured threshold."
                        )

                    st.markdown("#### What Does This Mean?")

                    st.write(
                        f"Control A converted **{a['conversion_rate']:.2%}** "
                        f"of assigned users, compared with "
                        f"**{b['conversion_rate']:.2%}** for Treatment B."
                    )

                    st.write(
                        f"The estimated absolute difference is "
                        f"**{stats['absolute_difference'] * 100:+.2f} "
                        f"percentage points**, with a p-value of "
                        f"**{p_value:.4f}**."
                    )

                    if significant:
                        st.caption(
                            "The observed difference meets the configured "
                            "statistical significance threshold. "
                            "This alone does not establish practical value "
                            "or guarantee that rollout is appropriate."
                        )
                    else:
                        st.caption(
                            "The available evidence does not establish "
                            "a statistically significant difference. "
                            "This does not prove the variants are equivalent."
                        )


                        if not stats["normal_approximation_valid"]:
                            st.warning(
                                "The normal approximation assumptions "
                                "are not satisfied. Interpret the "
                                "z-test results cautiously."
                            )

                        # 4. Confidence interval
                        st.markdown("#### Confidence Interval")

                        ci = stats["confidence_interval"]

                        lower = ci["lower"] * 100
                        upper = ci["upper"] * 100
                        estimate = stats["absolute_difference"] * 100

                        ci_fig = go.Figure()

                        ci_fig.add_trace(
                            go.Scatter(
                                x=[estimate],
                                y=["Treatment B vs Control A"],
                                mode="markers",
                                marker=dict(
                                    size=12,
                                    color="#2563EB",
                                ),
                                error_x=dict(
                                    type="data",
                                    symmetric=False,
                                    array=[upper - estimate],
                                    arrayminus=[estimate - lower],
                                    color="#2563EB",
                                    thickness=3,
                                    width=8,
                                ),
                                hovertemplate=(
                                    "Estimated difference: %{x:.2f} pp"
                                    "<extra></extra>"
                                ),
                            )
                        )

                        ci_fig.add_vline(
                            x=0,
                            line_dash="dash",
                            line_color="#94A3B8",
                        )

                        ci_fig.update_layout(
                            height=220,
                            margin=dict(l=20, r=20, t=15, b=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis_title="Absolute Difference (pp)",
                            font=dict(color="#334155"),
                            showlegend=False,
                        )

                        st.plotly_chart(
                            ci_fig,
                            use_container_width=True,
                        )

                        confidence_level = (1 - alpha) * 100

                        st.caption(
                            f"{confidence_level:.0f}% confidence interval: "
                            f"{lower:+.2f} to {upper:+.2f} percentage "
                            "points (Treatment B minus Control A)."
                        )

                        st.caption(
                            "Statistical significance alone does not "
                            "establish practical business value. "
                            "Review experiment health before making "
                            "a release decision."
                        )




        with summary_tab:
            st.subheader("Experiment Summary")

            # ------------------------------------------
            # SAMPLE SIZE PROGRESS
            # ------------------------------------------

            st.markdown("#### Sample Size Progress")

            planned = experiment.get("planned_sample_size")

            try:
                metrics_data = get_experiment_metrics(experiment_id)

                # Count users assigned to each variant.
                # Adjust this extraction if your metrics API
                # uses a different response structure.

                variant_metrics = metrics_data.get("variants", {})

                collected = sum(
                    int(data.get("assigned_users", 0))
                    for data in variant_metrics.values()
                )


                if planned is not None:
                    progress = min(collected / planned, 1.0)

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Users Collected",
                        f"{collected:,}",
                    )
                    col2.metric(
                        "Planned Users",
                        f"{planned:,}",
                    )
                    col3.metric(
                        "Progress",
                        f"{collected / planned * 100:.1f}%",
                    )

                    st.progress(progress)

                    if collected < planned:
                        st.caption(
                            f"{planned - collected:,} more users "
                            "needed to reach the planned sample size."
                        )
                    else:
                        st.success(
                            "Planned sample size reached. "
                            "Review statistical results and "
                            "experiment health before rollout."
                        )

                else:
                    st.metric(
                        "Users Collected",
                        f"{collected:,}",
                    )
                    st.info(
                        "No planned sample size was configured. "
                        "A pre-specified stopping target is needed "
                        "for sample-size-based decision readiness."
                    )


            except APIClientError as exc:
                st.error(
                    f"Unable to load sample-size progress: {exc}"
                )

            # ------------------------------------------
            # DECISION ENGINE
            # ------------------------------------------

            st.markdown("#### Decision Recommendation")

            if experiment["status"] == "draft":
                st.info(
                    "This experiment is still a draft. "
                    "Start the experiment and collect data "
                    "before evaluating a rollout decision."
                )

            else:
                try:
                    decision_data = get_experiment_decision(
                        experiment_id
                    )

                except APIClientError as exc:
                    st.error(str(exc))

                else:
                    decision = decision_data["decision"]
                    health_status = decision_data["health_status"]
                    reason = decision_data["reason"]

                    if decision == "rollout_b":
                        st.success(
                            "Recommendation: Roll Out Variant B"
                        )
                    elif decision == "keep_a":
                        st.warning(
                            "Recommendation: Keep Variant A"
                        )
                    elif decision == "continue_experiment":
                        st.info(
                            "Recommendation: Continue Experiment"
                        )
                    elif decision == "investigate":
                        st.warning(
                            "Recommendation: Investigate Experiment"
                        )
                    else:
                        st.info(
                            f"Recommendation: "
                            f"{decision.replace('_', ' ').title()}"
                        )

                    st.write(
                        "**Decision Engine Output:**",
                        decision.replace("_", " ").title(),
                    )
                    st.write(
                        "**Health Status:**",
                        health_status.replace("_", " ").title(),
                    )
                    st.write("**Reason:**", reason)


    elif st.session_state.get("show_create_experiment", False):


        # ------------------------------------------
        # CREATE EXPERIMENT VIEW
        # ------------------------------------------

        if st.button(
            "Back to Experiments",
            icon=":material/arrow_back:",
            type="tertiary",
        ):
            st.session_state.show_create_experiment = False
            st.rerun()

        st.title("Create New Experiment")
        st.write("Configure a new A/B experiment.")

        with st.container(border=True):

            with st.form("create_experiment_form"):

                experiment_id = st.text_input(
                    "Experiment ID",
                    placeholder="checkout_redesign_v1",
                )

                experiment_name = st.text_input(
                    "Experiment Name",
                    placeholder="Checkout Redesign",
                )

                primary_metric = st.text_input(
                    "Primary Metric",
                    value="conversion_rate",
                )



                planned_sample_size = st.number_input(
                    "Planned Sample Size (Total Users)",
                    min_value=1,
                    value=12000,
                    step=1000,
                    help=(
                        "Set the total number of users required before "
                        "evaluating the final experiment decision. "
                        "Determine this target before starting the experiment."
                    ),
                )

                st.caption(
                    "The sample-size target should be calculated from your "
                    "baseline conversion rate, minimum detectable effect, "
                    "significance level, and statistical power."
                )


                st.markdown("**Traffic Allocation**")

                traffic_a = st.slider(
                    "Variant A (%)",
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=5,
                )

                traffic_b = 100 - traffic_a

                st.caption(
                    f"Variant A: {traffic_a}%  |  "
                    f"Variant B: {traffic_b}%"
                )

                submitted = st.form_submit_button(
                    "Create Experiment",
                    type="primary",
                )

                if submitted:

                    if (
                        not experiment_id.strip()
                        or not experiment_name.strip()
                        or not primary_metric.strip()
                    ):
                        st.error("Please complete all required fields.")

                    elif traffic_a in (0, 100):
                        st.error("Both variants must receive traffic.")

                    else:
                        try:

                            create_experiment(
                                experiment_id=experiment_id.strip(),
                                name=experiment_name.strip(),
                                variants={
                                    "A": traffic_a / 100,
                                    "B": traffic_b / 100,
                                },
                                primary_metric=primary_metric.strip(),
                                planned_sample_size=int(planned_sample_size),
                            )


                        except APIClientError as exc:
                            st.error(str(exc))

                        else:
                            st.session_state.show_create_experiment = False
                            st.session_state.experiment_created = True
                            st.rerun()

    else:

        # ------------------------------------------
        # EXPERIMENT LIST VIEW
        # ------------------------------------------

        title_col, button_col = st.columns([4, 1])

        with title_col:
            st.title("Experiments")

        with button_col:
            st.write("")

            if st.button(
                "New Experiment",
                icon=":material/add:",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.show_create_experiment = True
                st.rerun()

        st.write("Manage and monitor your A/B experiments.")

        if st.session_state.pop("experiment_created", False):
            st.success("Experiment created successfully!")

        try:
            experiments = get_experiments(token=st.session_state.access_token)
            api_error = None

        except APIClientError as exc:
            experiments = []
            api_error = str(exc)

        if api_error:
            st.error(f"Unable to load experiments: {api_error}")

        search_col, filter_col = st.columns([3, 1])

        with search_col:
            search_query = st.text_input(
                "Search experiments",
                placeholder="Search by name or experiment ID",
            )

        with filter_col:
            status_filter = st.selectbox(
                "Status",
                ["All", "Draft", "Running", "Completed"],
            )

        filtered_experiments = [
            experiment
            for experiment in experiments
            if (
                search_query.lower()
                in (
                    experiment["name"] + " "
                    + experiment["experiment_id"]
                ).lower()
            )
            and (
                status_filter == "All"
                or experiment["status"].lower()
                == status_filter.lower()
            )
        ]

        st.caption(
            f"Showing {len(filtered_experiments)} "
            f"of {len(experiments)} experiments"
        )

        if filtered_experiments:

            rows = []

            for experiment in filtered_experiments:
                rows.append(
                    {
                        "Experiment": experiment["name"],
                        "Experiment ID": experiment["experiment_id"],
                        "Status": experiment["status"].title(),
                        "Primary Metric": experiment["primary_metric"],
                        "Variants": " / ".join(
                            f"{variant}: {weight:.0%}"
                            for variant, weight
                            in experiment["variants"].items()
                        ),
                    }
                )


            selection = st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="experiments_table",
            )

            if selection.selection.rows:
                selected_index = selection.selection.rows[0]

                selected_experiment = filtered_experiments[
                    selected_index
                ]

                st.session_state.selected_experiment_id = (
                    selected_experiment["experiment_id"]
                )

                st.rerun()


        elif not api_error:
            st.info("No experiments match your filters.")



# --------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------


elif page == "Results":

    st.caption("ANALYTICS / RESULTS")
    st.title("Statistical Results")

    st.write(
        "Compare experiment performance and "
        "evaluate statistical significance."
    )

    try:
        experiments = get_experiments(token=st.session_state.access_token)
    except APIClientError as exc:
        st.error(str(exc))
    else:
        if not experiments:
            st.info("No experiments available.")
        else:
            experiment_options = {
                exp["experiment_id"]: exp
                for exp in experiments
            }

            selected_id = st.selectbox(
                "Select Experiment",
                options=list(experiment_options),
                format_func=lambda exp_id: (
                    experiment_options[exp_id]["name"]
                ),
                key="results_experiment_selector",
            )

            st.divider()

            try:
                metrics = get_experiment_metrics(selected_id)
                statistics_response = (
                    get_experiment_statistics(selected_id)
                )
            except APIClientError as exc:
                st.error(str(exc))
            else:
                variants = metrics["variants"]

                a = variants["A"]
                b = variants["B"]

                total_users = (
                    a["assigned_users"]
                    + b["assigned_users"]
                )

                if total_users == 0:
                    st.info(
                        "No experiment data available yet."
                    )
                else:
                    st.subheader("Performance Overview")

                    lift = metrics["relative_lift_percent"]

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Control A",
                        f"{a['conversion_rate']:.2%}",
                    )
                    c2.metric(
                        "Treatment B",
                        f"{b['conversion_rate']:.2%}",
                    )

                    c3.metric(
                        "SRM Detected",
                        (
                            "Not evaluated"
                            if srm["has_srm"] is None
                            else "Yes" if srm["has_srm"] else "No"
                        ),
                    )

                    c4.metric(
                        "Users",
                        f"{total_users:,}",
                    )

                    st.subheader("Conversion Rate Comparison")

                    import plotly.graph_objects as go

                    fig = go.Figure()

                    fig.add_bar(
                        x=["Control A", "Treatment B"],
                        y=[
                            a["conversion_rate"] * 100,
                            b["conversion_rate"] * 100,
                        ],
                        marker_color=[
                            "#94A3B8",
                            "#2563EB",
                        ],
                        text=[
                            f"{a['conversion_rate']:.2%}",
                            f"{b['conversion_rate']:.2%}",
                        ],
                        textposition="outside",
                    )

                    fig.update_layout(
                        height=350,
                        yaxis_title="Conversion Rate (%)",
                        showlegend=False,
                        margin=dict(
                            l=20, r=20, t=25, b=20
                        ),
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch",
                    )

                    st.subheader("Statistical Significance")

                    if statistics_response is None:
                        st.info(
                            "Insufficient data for statistical analysis."
                        )
                    else:
                        stats = statistics_response["statistics"]

                        s1, s2, s3 = st.columns(3)

                        s1.metric(
                            "P-value",
                            f"{stats['p_value']:.6f}",
                        )

                        s2.metric(
                            "SRM Threshold",
                            f"{srm['alpha']:.3f}"
                            if srm["alpha"] is not None
                            else "N/A",
                        )

                        s3.metric(
                            "Significance Level",
                            f"{stats['alpha']:.2f}",
                        )

                        if stats["is_significant"]:
                            st.success(
                                "Statistically significant "
                                "difference detected."
                            )
                        else:
                            st.info(
                                "No statistically significant "
                                "difference detected."
                            )

                        ci = stats["confidence_interval"]

                        st.write(
                            "**Confidence Interval:** "
                            f"{ci['lower'] * 100:+.2f} to "
                            f"{ci['upper'] * 100:+.2f} "
                            "percentage points."
                        )

                        if not stats["normal_approximation_valid"]:
                            st.warning(
                                "Normal approximation assumptions "
                                "are not satisfied."
                            )

                        st.caption(
                            "Statistical significance does not "
                            "automatically justify rollout. "
                            "Review experiment health and "
                            "the decision recommendation."
                        )


# --------------------------------------------------
# HEALTH PAGE
# --------------------------------------------------


elif page == "Health":

    st.caption("MONITORING / HEALTH")
    st.title("Experiment Health")

    st.write(
        "Monitor sample ratio mismatch, traffic allocation, "
        "and experiment data quality."
    )

    try:
        experiments = get_experiments(token=st.session_state.access_token)
    except APIClientError as exc:
        st.error(str(exc))
    else:
        if not experiments:
            st.info("No experiments available.")
        else:
            experiment_options = {
                exp["experiment_id"]: exp
                for exp in experiments
            }

            selected_id = st.selectbox(
                "Select Experiment",
                options=list(experiment_options),
                format_func=lambda exp_id: (
                    experiment_options[exp_id]["name"]
                ),
                key="health_experiment_selector",
            )

            st.divider()

            try:
                health = get_experiment_health(selected_id)
            except APIClientError as exc:
                st.error(str(exc))
            else:

                status = health["status"]
                validation = health["validation"]
                srm = health.get("srm")

                if srm is None:
                    srm = {
                        "has_srm": None,
                        "p_value": None,
                        "alpha": None,
                        "chi_square": None,
                        "total_users": 0,
                        "observed_counts": {},
                        "expected_weights": {},
                    }


                st.subheader("Health Overview")

                c1, c2, c3 = st.columns(3)


                display_status = (
                    "Awaiting Data"
                    if validation["total_users"] == 0
                    else status.replace("_", " ").title()
                )

                c1.metric(
                    "Health Status",
                    display_status,
                )

                c2.metric(
                    "Total Users",
                    f"{validation['total_users']:,}",
                )

                c3.metric(
                    "SRM Detected",
                    (
                        "Not evaluated"
                        if srm["has_srm"] is None
                        else "Yes" if srm["has_srm"] else "No"
                    ),
                )


                if validation["total_users"] == 0:
                    st.info(
                        "Awaiting experiment data. Health checks "
                        "will become meaningful after users "
                        "are assigned."
                    )
                elif status == "healthy":
                    st.success(
                        "Experiment health checks passed."
                    )
                else:
                    st.warning(
                        "Experiment health requires investigation."
                    )

                st.subheader("Sample Ratio Mismatch")

                s1, s2, s3 = st.columns(3)

                s1.metric(
                    "SRM P-value",
                    f"{srm['p_value']:.6f}"
                    if srm["p_value"] is not None
                    else "N/A",
                )


                s2.metric(
                    "SRM Threshold",
                    (
                        f"{srm['alpha']:.3f}"
                        if srm["alpha"] is not None
                        else "N/A"
                    ),
                )


                s3.metric(
                    "Chi-square",
                    f"{srm['chi_square']:.4f}"
                    if srm["chi_square"] is not None
                    else "N/A",
                )


                st.subheader("Traffic Allocation")

                total = srm["total_users"]

                if total == 0:
                    st.info(
                        "No assignment data available yet. "
                        "The traffic allocation chart will appear "
                        "once users are assigned."
                    )


                else:

                    import plotly.graph_objects as go

                    observed = srm["observed_counts"]
                    expected = srm["expected_weights"]
                    total = srm["total_users"]

                    variant_names = list(expected.keys())

                    expected_counts = [
                        total * expected[name]
                        for name in variant_names
                    ]

                    observed_counts = [
                        observed.get(name, 0)
                        for name in variant_names
                    ]

                    fig = go.Figure()

                    fig.add_bar(
                        name="Expected",
                        x=variant_names,
                        y=expected_counts,
                        marker_color="#94A3B8",
                    )

                    fig.add_bar(
                        name="Observed",
                        x=variant_names,
                        y=observed_counts,
                        marker_color="#2563EB",
                    )

                    fig.update_layout(
                        barmode="group",
                        height=350,
                        yaxis_title="Assigned Users",
                        margin=dict(l=20, r=20, t=25, b=20),
                        legend=dict(orientation="h"),
                    )

                    st.plotly_chart(fig, width="stretch")

                st.subheader("Data Validation")


                if validation["total_users"] == 0:
                    st.info(
                        "Validation is pending because the experiment "
                        "has no assigned users."
                    )
                elif validation["is_valid"]:
                    st.success("Data validation passed.")
                else:
                    st.error("Data validation failed.")


                issues = validation.get("issues", [])

                if issues:
                    for issue in issues:
                        st.warning(str(issue))
                else:
                    st.caption(
                        "No validation issues reported."
                    )

                st.caption(
                    "SRM checks whether observed assignment "
                    "counts are consistent with the expected "
                    "traffic allocation. A detected mismatch "
                    "may indicate assignment or tracking issues."
                )


# --------------------------------------------------
# DECISIONS PAGE
# --------------------------------------------------


elif page == "Decisions":

    st.caption("ANALYTICS / DECISIONS")
    st.title("Decision Intelligence")

    st.write(
        "Review experiment recommendations, statistical "
        "evidence, and sample-size readiness."
    )

    try:
        experiments = get_experiments(token=st.session_state.access_token)
    except APIClientError as exc:
        st.error(str(exc))
    else:
        if not experiments:
            st.info("No experiments available.")
        else:
            experiment_options = {
                exp["experiment_id"]: exp
                for exp in experiments
            }

            selected_id = st.selectbox(
                "Select Experiment",
                options=list(experiment_options),
                format_func=lambda exp_id: (
                    experiment_options[exp_id]["name"]
                ),
                key="decisions_experiment_selector",
            )


            experiment = experiment_options[selected_id]

            try:
                experiment_details = get_experiment(selected_id)
            except APIClientError as exc:
                st.error(
                    f"Could not load experiment details: {exc}"
                )
                st.stop()



            st.divider()

            try:
                metrics = get_experiment_metrics(selected_id)
                decision_data = get_experiment_decision(selected_id)
                health = get_experiment_health(selected_id)
            except APIClientError as exc:
                st.error(str(exc))
            else:
                variants = metrics["variants"]

                collected = sum(
                    item["assigned_users"]
                    for item in variants.values()
                )

                planned = experiment_details.get("planned_sample_size")
                decision = decision_data["decision"]
                health_status = decision_data["health_status"]
                reason = decision_data["reason"]

                st.subheader("Decision Overview")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Users Collected",
                    f"{collected:,}",
                )
                c2.metric(
                    "Planned Sample Size",
                    f"{planned:,}" if planned else "Not set",
                )
                c3.metric(
                    "Experiment Health",
                    (
                        "Awaiting Data"
                        if collected == 0
                        else health_status.replace("_", " ").title()
                    ),
                )

                st.subheader("Sample Size Readiness")

                if planned:
                    progress = min(collected / planned, 1.0)
                    st.progress(progress)

                    st.caption(
                        f"{collected:,} of {planned:,} users collected "
                        f"({collected / planned * 100:.1f}%)."
                    )

                    if collected < planned:
                        st.info(
                            f"{planned - collected:,} additional users "
                            "needed to reach the planned sample size."
                        )
                    else:
                        st.success(
                            "Planned sample size reached."
                        )
                else:
                    st.info(
                        "No planned sample size was configured. "
                        "A pre-specified sample size is needed "
                        "for sample-size-based decision readiness."
                    )

                st.subheader("Decision Recommendation")

                if collected == 0:
                    st.info(
                        "Awaiting experiment data. A rollout "
                        "decision cannot be evaluated yet."
                    )
                elif decision == "rollout_b":
                    st.success(
                        "Recommendation: Roll Out Variant B"
                    )
                elif decision == "keep_a":
                    st.warning(
                        "Recommendation: Keep Variant A"
                    )
                elif decision == "continue_experiment":
                    st.info(
                        "Recommendation: Continue Experiment"
                    )
                elif decision == "investigate":
                    st.warning(
                        "Recommendation: Investigate Experiment"
                    )
                else:
                    st.info(
                        f"Recommendation: "
                        f"{decision.replace('_', ' ').title()}"
                    )

                st.write("**Decision Engine Output:**",
                         decision.replace("_", " ").title())
                st.write("**Reason:**", reason)

                st.subheader("Decision Evidence")

                st.write(
                    "**Health Status:**",
                    health["status"].replace("_", " ").title(),
                )

                st.write(
                    "**Data Validation:**",
                    "Passed"
                    if health["validation"]["is_valid"]
                    else "Not passed",
                )

                srm = health.get("srm")

                st.write(
                    "**Sample Ratio Mismatch:**",
                    (
                        "Not evaluated"
                        if srm is None
                        else "Detected"
                        if srm["has_srm"]
                        else "Not detected"
                    ),
                )

                st.caption(
                    "A statistically significant result alone "
                    "does not guarantee that rollout is appropriate. "
                    "Experiment health, sample-size readiness, "
                    "and business impact should also be considered."
                )
