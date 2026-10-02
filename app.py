"""Entry point. Run with: streamlit run app.py"""
import streamlit as st

from charts import load_report

st.set_page_config(page_title="Personalisation Lift", page_icon=":material/recommend:")

pages = [
    st.Page("views/lift.py", title="Lift", icon=":material/trending_up:", default=True),
    st.Page("views/who_benefits.py", title="Who benefits", icon=":material/groups:", url_path="who-benefits"),
    st.Page("views/why.py", title="Popularity or fit", icon=":material/call_split:", url_path="popularity-or-fit"),
]
page = st.navigation(pages)

report = load_report()
with st.sidebar:
    st.subheader("About")
    st.write("For two weeks a video app swapped some recommended videos for random ones. "
             "Comparing the two shows what the recommender is worth.")
    st.write("**Who benefits** splits the result by user type. "
             "**Popularity or fit** asks where the gain comes from.")
    st.caption(f"Data: KuaiRand-Pure, {report['users_total']:,} users, "
               f"{report['exposures']['recommended'] + report['exposures']['random']:,} videos shown, "
               "22 April to 8 May 2022.")

page.run()
