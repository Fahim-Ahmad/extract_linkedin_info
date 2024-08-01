import streamlit as st
from linkedin_api import Linkedin
import pandas as pd
from datetime import date
import base64

# custome function to fetch linkedin info
def fetch_linkedin_info(profile_ids):
    linkedin_info = {}
    
    for profile_id in profile_ids:
        
        profile = api.get_profile(profile_id)
        profile_info = {
            'name': f"{profile['firstName'] if 'firstName' in profile else None} {profile['lastName'] if 'lastName' in profile else ''}",
            'headline': profile['headline'] if 'headline' in profile else None,
            'summary' : profile['summary'] if 'summary' in profile else None,
            'industry_name': profile['industryName'] if 'industryName' in profile else None
        }

        skills = api._fetch(f"/identity/profiles/{profile_id}/skills").json().get('elements', [])
        skill_names = [i['name'] if 'name' in i else '' for i in skills]

        educations = api._fetch(f"/identity/profiles/{profile_id}/educations").json().get('elements', [])
        education = [{
            'degreeName': [i['degreeName'] if 'degreeName' in i else None for i in educations][n],
            'schoolName': [i['schoolName'] if 'schoolName' in i else None for i in educations][n],
            'startYear': [i['timePeriod']['startDate']['year'] if 'startDate' in i['timePeriod'] else None for i in educations][n],
            'endYear': [i['timePeriod']['endDate']['year'] if 'endDate' in i['timePeriod'] else None for i in educations][n],
        } for n in range(len(educations))]

        experiences = api._fetch(f"/identity/profiles/{profile_id}/positions").json().get('elements', [])
        experience = [{
            'title': [i['title'] if 'title' in i else None for i in experiences][n],
            'companyName': [i['companyName'] if 'companyName' in i else None for i in experiences][n],
            'startYear': [i['timePeriod']['startDate']['year'] if 'startDate' in i['timePeriod'] else None for i in experiences][n],
            'endYear': [i['timePeriod']['endDate']['year'] if 'endDate' in i['timePeriod'] else 'Present' for i in experiences][n],
        } for n in range(len(experiences))]

        linkedin_info[profile_id] = {
                'profile_info': profile_info,
                'skills': skill_names,
                'educations': education,
                'experiences': experience
            }

    return linkedin_info

# streamlit app
linkedin_email = st.sidebar.text_input("Please Enter Your LinkedIn Email")
linkedin_password = st.sidebar.text_input("Please Enter Your LinkedIn Password", type="password")
profile_id = st.sidebar.text_input("Please Enter a LinkedIn Profile ID")

if st.sidebar.button("Fetch Info"):

    try:
        api = Linkedin(linkedin_email, linkedin_password)
        linkedin_info = fetch_linkedin_info([profile_id])
        user = linkedin_info[profile_id]

        if user['profile_info']['headline'] and user['profile_info']['summary'] and user['profile_info']['industry_name']:
            st.header(user['profile_info']['name'])
            st.header(user['profile_info']['headline'])
            st.write(f"**About**: {user['profile_info']['summary']}")

            df = pd.DataFrame([user])
            csv_file_name = f"output/linkedin_info-{date.today()}.csv"
            b64 = base64.b64encode(df.to_csv(index=False).encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{csv_file_name}">Download LinkedIn Info</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("This profile can't be accessed.\nPlease make sure to enter a valid user id")
            
        if 'skills' in user and len(user['skills']) > 0:
            st.header("**Skills**:")
            st.write(", ".join(user['skills']))

        if 'educations' in user and len(user['educations']) > 0:
            st.header("**Education**:")
            for edu in user['educations']:
                st.write(f"- {edu['degreeName']} ({edu['schoolName']}, {edu['startYear']}-{edu['endYear']}\n")

        if 'experiences' in user and len(user['experiences']) > 0:
            st.header("**Experience**:")
            for exp in user['experiences']:
                st.write(f"- {exp['title']} ({exp['companyName']}, {exp['startYear']}-{exp['endYear']}\n")

        # st.json(linkedin_info[profile_id])
        

    except Exception as e:
        st.sidebar.error(f"Failed to connect: {str(e)}")

# execute 'streamlit run app.py' in terminal to run the app
# execute 'pip freeze > requirements.txt' to generate the requirements file