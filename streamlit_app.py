# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
fruit_rows = my_dataframe.collect()

fruit_name_to_search = {}
fruit_display_names = []

for row in fruit_rows:
    fruit_display_names.append(row["FRUIT_NAME"])
    fruit_name_to_search[row["FRUIT_NAME"]] = row["SEARCH_ON"]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_display_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        try:
            search_on = fruit_name_to_search[fruit_chosen]

            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        except Exception as e:
            st.write("Sorry, that fruit is not available in the API.")

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
