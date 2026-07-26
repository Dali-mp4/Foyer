import pandas as pd
import streamlit as st
from db import get_connection

conn = get_connection()
mycursor = conn.cursor()

st.title("Gerer les etudiantes")
query = "SELECT * FROM students"

df = pd.read_sql(query, conn)



#search
search = st.text_input("Search")

if search:
    df = df[
        df["nom"].str.contains(search, case=False, na=False) |
        df["prenom"].str.contains(search, case=False, na=False) |
        df["national_id"].astype(str).str.contains(search, na=False) |
        df["tel"].str.contains(search, case=False, na=False)
        
    ]




#delete students par dropbox
mycursor.execute("""
SELECT national_id, nom, prenom
FROM students
""")

students = mycursor.fetchall()

student_dict = {
    f"{student[1]} {student[2]} (ID: {student[0]})": student[0]
    for student in students
}

selected_student = st.selectbox(
    "Select a student to delete",
    list(student_dict.keys())
)

if st.button("Effacer etudiante"):
    national_id = student_dict[selected_student]

    mycursor.execute(
        "DELETE FROM students WHERE national_id = %s",
        (national_id,)
    )

    conn.commit()

    st.success("Student deleted successfully!")




#update students in data frame
df["Delete"] = False

edited_df = st.data_editor(
    df, 
    num_rows="dynamic",
    use_container_width=True
)


df = pd.read_sql("SELECT * FROM students", conn)

if st.button("Appliquer"):
    for _, row in edited_df.iterrows():
            if row["Delete"]:
                mycursor.execute(
                    "DELETE FROM students WHERE national_id = %s",
                    (int(row["national_id"]),)
                )

    # Compare original and edited data
    for index in range(len(df)):

        original = df.iloc[index]
        edited = edited_df.iloc[index]

        # Skip deleted rows
        if edited["Delete"]:
            continue

        if not edited.equals(original):
            if len(edited["national_id"]) == 8 and len(edited["tel"]) == 8:
                mycursor.execute("""
                    UPDATE students
                    SET
                        nom=%s,
                        prenom=%s,
                        tel=%s,
                        national_id=%s
                    WHERE national_id=%s
                """,(
                    str(edited["nom"]),
                    str(edited["prenom"]),
                    str(edited["tel"]),
                    str(edited["national_id"]),
                    str(original["national_id"])
                ))
            else:
                st.error("L'identifiant ou le numero du tel doit comporter 8 chiffres.")
                st.stop()
    if len(edited_df) > len(df):

        new_rows = edited_df.iloc[len(df):]

        for _, row in new_rows.iterrows():
            
            # Ignore empty rows
            if pd.isna(row["national_id"]):
                continue
            if len(row["national_id"]) == 8 and len(row["tel"]) == 8:
                mycursor.execute("""
                    INSERT INTO students
                    (nom, prenom, national_id, tel)
                    VALUES (%s,%s,%s,%s)
                """,(
                    row["nom"],
                    row["prenom"],
                    row["national_id"],
                    row["tel"]
                ))
            else:
                    st.error("L'identifiant ou le numero du tel doit comporter 8 chiffres.")
                    st.stop()
    conn.commit()
    mycursor.close()

    st.success("Changes saved!")
    time.sleep(1)
    st.rerun()

