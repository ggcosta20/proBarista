import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import calendar
import os
import streamlit.components.v1 as components
from streamlit_image_select import image_select
PASSWORD ="bestbaristainlondon"

# Set up the app theme and layout
st.set_page_config(page_title="Barista Profile", page_icon="☕", layout="wide")

# Custom CSS for black theme and skill cards
st.markdown(
    """
    <style>
.about-me-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .profile-pic {
        width: 150px; /* Size of the profile picture */
        height: 150px;
        border-radius: 50%; /* Round shape */
        object-fit: cover;
        object-position: top; /* Adjust position to prevent head cutoff */
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3); /* Optional shadow effect */
    }
    .about-me-text {
        color: #ffffff;
    }

    
    
    /* Black background for the app */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    /* Skill cards styling */
    .skill-card {
        background-color: #222222;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 10px 0;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
        cursor: pointer;
    }
    .skill-card h3 {
        color: #80ffea;
    }
    .skill-icon {
        font-size: 30px;
        margin-right: 10px;
        color: #80ffea;
    }
    /* Basic gallery grid styling */
    .gallery-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        padding: 20px;
    }
    .gallery-item {
        overflow: hidden;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .gallery-item:hover {
        transform: scale(1.05);
    }
    .gallery-item img, .gallery-item video {
        width: 100%;
        height: auto;
        border-radius: 8px;
    }
    
    
    
      .calendar-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        padding: 10px;
        text-align: center;
    }
    .day-cell {
        background-color: #333333;
        color: #ffffff;
        border-radius: 8px;
        padding: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s;
    }
    .day-cell:hover {
        background-color: #444444;
        transform: scale(1.05);
    }
    .available {
        background-color: #2e8b57;
    }
    .unavailable {
        background-color: #b22222;
    }
    .weekday {
        font-size: 0.8em;
        color: #80ffea;
    }
    .book-button {
        background-color: #80ffea;
        border: none;
        color: #000000;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.8em;
    }
    
      /* Status badges */
    .date-available { 
        background-color: #2e8b57; /* Green for available */ 
        color: white; 
        padding: 5px; 
        border-radius: 5px; 
        text-align: center;
    }
    .date-booked { 
        background-color: #b22222; /* Red for booked */ 
        color: white; 
        padding: 5px; 
        border-radius: 5px; 
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #80ffea; /* Light blue */
        color: #000000; /* Black text */
        border-radius: 5px;
        padding: 10px 15px;
        border: none;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    
    /* Hover effect for buttons */
    .stButton > button:hover {
        background-color: #66e0d3; /* Slightly darker shade on hover */
    }
    
    /* Specific button for cancel action */
    .stButton > button.cancel-button {
        background-color: #b22222; /* Red for cancel */
        color: white;
    }
    .stButton > button.cancel-button:hover {
        background-color: #a02020; /* Darker red on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Database connection function
def create_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your database host
            database="barista_db",  # Replace with your database name
            user="root",  # Replace with your database username
            password="testW!R37"  # Replace with your database password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


# Function to fetch booked dates and times
def get_booked_dates():
    """Fetch booked dates and times from the MySQL database."""
    connection = create_connection()
    booked_dates = {}

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT preferred_date, preferred_time FROM bookings
                WHERE status = 'Booked'
            """
            cursor.execute(query)
            results = cursor.fetchall()

            for row in results:
                date_str = row['preferred_date'].strftime("%Y-%m-%d")
                time_str = row['preferred_time'].strftime("%I:%M %p")

                if date_str in booked_dates:
                    booked_dates[date_str].append(time_str)
                else:
                    booked_dates[date_str] = [time_str]

        except Error as e:
            print("Error fetching booked dates:", e)
        finally:
            cursor.close()
            connection.close()

    return booked_dates

# Function to fetch all bookings
def fetch_all_bookings():
    connection = create_connection()
    bookings = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM bookings"
            cursor.execute(query)
            bookings = cursor.fetchall()
        except Error as e:
            st.error("Failed to fetch bookings")
        finally:
            cursor.close()
            connection.close()
    return bookings


# Function to update a booking
def update_booking(booking_id, business_name, reporting_to, contact_number, address, shift_start_time, hours,
                   preferred_date):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            UPDATE bookings
            SET business_name = %s, reporting_to = %s, contact_number = %s, address = %s, shift_start_time = %s, hours = %s, preferred_date = %s
            WHERE id = %s
            """
            data = (
            business_name, reporting_to, contact_number, address, shift_start_time, hours, preferred_date, booking_id)
            cursor.execute(query, data)
            connection.commit()
            st.success("Booking updated successfully!")
        except Error as e:
            st.error("Failed to update booking")
        finally:
            cursor.close()
            connection.close()


# Function to delete a booking
def delete_booking(booking_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM bookings WHERE id = %s"
            cursor.execute(query, (booking_id,))
            connection.commit()
            st.success("Booking deleted successfully!")
        except Error as e:
            st.error("Failed to delete booking")
        finally:
            cursor.close()
            connection.close()


# Function to insert booking into the database
def insert_booking(business_name, reporting_to, contact_number, address, shift_start_time, hours, preferred_date):
    """Insert a new booking into the database."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO bookings (business_name, reporting_to, contact_number, address, shift_start_time, hours, preferred_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (business_name, reporting_to, contact_number, address, shift_start_time, hours, preferred_date, 'Booked')
            cursor.execute(query, data)
            connection.commit()
            st.success("Booking has been added to the database.")
        except Error as e:
            st.error("Failed to insert booking into the database.")
        finally:
            cursor.close()
            connection.close()






# Initialize session state variable for selected booking date
if "selected_booking_date" not in st.session_state:
    st.session_state["selected_booking_date"] = None

# Add "Manage Bookings" option in the navigation
selected_page = option_menu(
    menu_title=None,
    options=["About Me", "Gallery", "Availability & Pricing", "Bookings", "Manage Bookings"],
    icons=["house", "camera", "calendar", "clipboard-check", "tools"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#111111"},
        "nav-link": {"font-size": "18px", "color": "#ffffff"},
        "nav-link-selected": {"background-color": "#80ffea", "color": "#000000"},
    }
)


# Display different content based on the selected page

# Manage Bookings Page

# Manage Bookings Page
if selected_page == "Manage Bookings":
    # Prompt for the password
    password = st.text_input("Enter password to access Manage Bookings:", type="password")
    if password == PASSWORD:
        st.success("Access granted")
        # Add the code here to display and manage bookings
        st.write("Here are your bookings...")



        st.title("Manage Bookings")

        # Fetch and display all bookings
        bookings = fetch_all_bookings()
        if not bookings:
            st.write("No bookings available.")

        else:
            for booking in bookings:
                with st.expander(f"Booking ID: {booking['id']} - {booking['business_name']}"):
                    # Check if start_time is a timedelta and convert if necessary
                    start_time_value = (
                        (datetime.min + booking['start_time']).time()
                        if isinstance(booking['start_time'], timedelta)
                        else booking['start_time']
                    )

                    # Display time input with adjusted value
                    start_time = st.time_input("Start Time", value=start_time_value)
                    business_name = st.text_input("Business Name", value=booking['business_name'],
                                                  key=f"business_name_{booking['id']}")
                    reporting_to = st.text_input("Reporting To", value=booking['reporting_to'],
                                                 key=f"reporting_to_{booking['id']}")
                    contact_number = st.text_input("Contact Number", value=booking['phone'],
                                                   key=f"contact_number_{booking['id']}")
                    address = st.text_area("Address", value=booking['address'], key=f"address_{booking['id']}")
                    shift_start_time = st.time_input("Shift Start Time",
                                                     value=start_time_value,
                                                     key=f"shift_start_time_{booking['id']}")

                    hours = st.number_input("Hours", min_value=4, value=booking['hours'], key=f"hours_{booking['id']}")


                    # Update and delete buttons
                    if st.button("Update", key=f"update_{booking['id']}"):
                        update_booking(booking['id'], business_name, reporting_to, contact_number, address,
                                       shift_start_time, hours, preferred_date)
                    if st.button("Delete", key=f"delete_{booking['id']}"):
                        delete_booking(booking['id'])
    else:
        st.error("Incorrect password. Access denied.")


# Display different content based on the selected page
if selected_page == "About Me":
    st.title("About Me")

    # Display the profile picture with rounded styling and center alignment

    # Container with profile picture on the left and text on the right

    # Set up two columns
    col1, col2 = st.columns([1, 1])  # Adjust the column width ratio as needed

    # Left Column: Coffee Superpowers Meter and Customer Review
    with col1:
        st.markdown("### Coffee Superpowers Meter ☕️")
        st.markdown("Here's the breakdown of my coffee-making superpowers:")

        # Custom CSS for the coffee rating meter
        st.markdown(
            """
            <style>
            
                    .meter {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-family: Arial, sans-serif;
        }
        .meter-bar {
            background-color: #4b2e2e;
            border-radius: 5px;
            height: 8px;
            width: 100px;
            margin-left: 8px;
            position: relative;
        }
        .meter-bar-fill {
            height: 100%;
            border-radius: 5px;
            background-color: #d2691e;
        }
        .meter-label {
            font-weight: bold;
            font-size: 0.9em;
            color: #f5deb3;
            min-width: 80px;
        }
        .bean-icon {
            font-size: 0.9em;
            color: #8b4513;
            margin-left: 5px;
        }
            
            
            .gif-container {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 10px;
            }
            .gif-container img {
                width: 250px; /* Set desired width */
                height: 50px; /* Set desired height */
                border-radius: 30px;
            }
             .rounded-image {
        width: 200px; /* Adjust width as needed */
        height: auto; /* Keeps aspect ratio */
        border-radius: 50%; /* Makes the image circular */
        display: block;
        margin: 0 auto;
    }
            </style>
           
            """,
            unsafe_allow_html=True
        )


        # Function to display each rating with custom label and humor
        def display_rating(label, percentage, funny_measure):
            st.markdown(f"""
                <div class="meter">
                    <span class="meter-label">{label} {funny_measure}</span>
                    <div class="meter-bar">
                        <div class="meter-bar-fill" style="width: {percentage}%;"></div>
                    </div>
                    <span class="bean-icon">{'☕' * (percentage // 20)}</span>
                </div>
            """, unsafe_allow_html=True)


        # Rating bars with funny measures and coffee beans
        display_rating("Precision", 100, "— Sharp as an espresso shot")
        display_rating("Love", 120, "— Overflowing")
        display_rating("Caffeine", 100, "— Enough to power a small village")
        display_rating("Consistency", 95, "— A pour-over every time")
        display_rating("Patience", 85, "— Slow-brew champion")


    # Right Column: GIF of the pour
    with col2:
        # Display the GIF in a custom container
        # Adjust width proportionally; this might help control perceived height
        st.markdown(f"""
            <img src="https://back.homecleaningcompany.london/cv/gif.gif" class="rounded-image">
            """, unsafe_allow_html=True)




    # Why Direct Hire
    st.subheader("Why Choose Direct Hire?")
    st.write("""
    By working with me directly, you’re ensuring that your coffee service is consistent, reliable, and handled by someone who genuinely cares about the craft. There's no mystery of "who’s going to walk through the door today"—you’re hiring someone with proven expertise who will show up ready to deliver high-quality coffee service every time.

    So, let’s take the guesswork out of staffing and create a coffee experience that’s both personal and professional. Plus, you won’t have to worry about any “agency fees” or middlemen; you’re working with me, one-to-one.
    """)

    # Closing with a Lighthearted Touch
    st.write("""
    *(And yes, I promise I won’t show up with mismatched socks!)* ☕
    """)

    # Skills & Expertise Section with Expandable Text
    st.header("Skills & Expertise")

    # Skill 1: Latte Art Mastery
    with st.expander("☕ Latte Art Mastery"):
        st.write("""
            With a refined eye for detail, I excel in creating beautiful and intricate latte art that enhances the coffee experience.
            From classic designs like rosettas and hearts to more complex patterns, my latte art adds a personal and professional touch to every cup.
            """)

    # Skill 2: Customer Engagement
    with st.expander("🤝 Customer Engagement"):
        st.write("""
            I understand that a great coffee experience is about more than just the drink—it's also about connecting with customers.
            My friendly, approachable demeanor helps me build rapport with guests, making them feel welcome and appreciated.
            I’m skilled at reading the room and adapting my service to create a memorable experience for each customer.
            """)

    # Skill 3: High-Volume Service Efficiency
    with st.expander("⚙️ High-Volume Service Efficiency"):
        st.write("""
            Having worked in high-traffic environments, I’m experienced in handling a high volume of orders while maintaining quality and speed.
            My workflow is optimized for efficiency, allowing me to manage busy service periods without sacrificing the quality of each drink.
            """)

    # Skill 4: Barista Training & Mentorship
    with st.expander("📈 Barista Training & Mentorship"):
        st.write("""
            I enjoy sharing my knowledge with others, and I’m skilled at training and mentoring new baristas.
            I can provide hands-on guidance in espresso extraction, milk frothing techniques, and customer service essentials,
            helping other baristas develop confidence and proficiency in their roles.
            """)

    # Skill 5: Adaptability Across Diverse Settings
    with st.expander("🌟 Adaptability Across Diverse Settings"):
        st.write("""
            From bustling local coffee shops to corporate events and fine dining venues, I’ve worked in a wide variety of environments.
            This versatility allows me to adapt my style and service to meet the unique needs of each setting, ensuring top-notch service regardless of the location.
            """)

    # Skill 6: Knowledge of Specialty Coffee
    with st.expander("🎓 Knowledge of Specialty Coffee"):
        st.write("""
            My experience spans the entire coffee journey—from selecting beans and understanding different brewing methods to mastering the perfect extraction.
            I’m passionate about specialty coffee and stay updated on industry trends, which helps me bring an elevated coffee experience to my clients.
            """)

    # Experience Overview
    st.subheader("Professional Experience")

    st.write("""
    - **Specialty Coffee Expertise**: I’ve spent over a decade honing my craft, specializing in the intricacies of espresso extraction, milk frothing, and latte art. My experience includes working as a Head Barista in specialty coffee shops, where I managed coffee quality and trained junior baristas.

    - **Versatile Work Settings**: Throughout my career, I've had the opportunity to work in a wide range of environments, from cozy local coffee shops and high-traffic city spots to corporate events, fine dining venues, and even in corporate buildings as a contracted barista.

    - **Customer Service**: My background in customer service, including prior experience working in a phone shop, has shaped my approach to coffee service. I believe in creating an inviting experience for each guest, tailored to their needs.

    - **Freelance Barista**: Currently, I work on a self-employed basis, allowing me to bring my skills directly to businesses and events across London. This profile is designed to simplify the hiring process, letting café managers connect with me directly without the hassle of agency intermediaries.

    - **Technical Skills**: As someone who’s always looking to improve, I’m skilled not only in coffee preparation but also in teaching others the fundamentals, from espresso extraction and grinder calibration to perfecting latte art.
    """)


# Gallery Page Design
if selected_page == "Gallery":

    # Path to the folder containing images and videos
    media_folder = "./img"

    # Retrieve all files in the media folder
    media_files = sorted([f for f in os.listdir(media_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.mp4'))])

    # Initialize session state for tracking the current index
    if "current_media_index" not in st.session_state:
        st.session_state.current_media_index = 0


    # Function to navigate to the previous media
    def previous_media():
        st.session_state.current_media_index = (st.session_state.current_media_index - 1) % len(media_files)


    # Function to navigate to the next media
    def next_media():
        st.session_state.current_media_index = (st.session_state.current_media_index + 1) % len(media_files)


    # Display current media item based on the index
    current_media = media_files[st.session_state.current_media_index]
    file_path = os.path.join(media_folder, current_media)

    # CSS to style images, videos, and buttons
    st.markdown(
        """
        <style>
        /* Media container styling */
        .media-container {
            position: relative;
            max-width: 90%;
            width: 80vw;
            max-height: 60vh;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        /* Image styling */
        .media-container img {
            border-radius: 10px;
            max-width: 100%;
            max-height: 60vh;
            object-fit: cover;
        }
        /* Video styling */
        .media-container video {
            border-radius: 10px;
            max-width: 100%;
            max-height: 60vh;
        }
        /* Button styling */
        .nav-button {
            background-color: #80ffea;
            color: #000000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            margin: 10px 5px; /* Add spacing between buttons */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display navigation buttons on top of the media
    st.markdown("<div class='media-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        st.button("⬅️ Previous", on_click=previous_media, key="prev_button")

    with col3:
        st.button("Next ➡️", on_click=next_media, key="next_button")
    st.markdown("</div>", unsafe_allow_html=True)

    # Display the current media item without displaying the file name
    if current_media.endswith(('.jpg', '.jpeg', '.png')):
        st.image(file_path, use_column_width=True)
    elif current_media.endswith('.mp4'):
        st.video(file_path)

elif selected_page == "Availability & Pricing":
    st.title("Availability & Pricing")


    # Set up the app theme and layout

    # Sample data for booked dates (replace with database query)
    today = datetime.now()
    booked_dates = {today + timedelta(days=i): "Booked" for i in range(0, 30, 5)}

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .date-available { background-color: #2e8b57; color: white; padding: 5px; border-radius: 5px; }
        .date-booked { background-color: #b22222; color: white; padding: 5px; border-radius: 5px; }
        .centered-text { text-align: center; }
        .form-container { padding: 10px; background-color: #333333; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Date Selection
    st.subheader("Availability Calendar")
    selected_date = st.date_input("Select a date to book")

    # Format selected date for comparison
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    status = "Available" if selected_date not in booked_dates else "Booked"
    status_class = "date-available" if status == "Available" else "date-booked"

    # Display availability status with conditional booking option
    st.markdown(f"<div class='{status_class} centered-text'>{status}</div>", unsafe_allow_html=True)

    if status == "Available":
        # Show booking form if available
        with st.expander("Book this date"):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            business_name = st.text_input("Business Name")
            reporting_to = st.text_input("Reporting To")
            contact_number = st.text_input("Contact Number")
            address = st.text_area("Address")
            shift_start_time = st.time_input("Shift Start Time")
            hours = st.number_input("Hours (Minimum 4)", min_value=4, value=4)

            # Calculate pricing
            hourly_rate = 18 if hours >= 6 else 20
            total_price = hours * hourly_rate

            #st.write(f"Hourly Rate: £{hourly_rate}")
            #st.write(f"Total Price: £{total_price}")

            # Booking actions

            if st.button("Confirm Booking"):
                try:
                    insert_booking(business_name, reporting_to, contact_number, address, shift_start_time, hours,
                                   total_price)
                    st.success("Booking confirmed!")
                except Exception as e:
                    st.error(f"Failed to insert booking into the database: {e}")

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Selected date is unavailable for booking.")
    # Custom CSS for the dark theme and calendar styling

    st.subheader("Pricing")
    st.write("I offer flexible pricing based on the duration of the booking:")
    st.write("- **£18 per hour** for bookings over 6 hours")
    st.write("- **£20 per hour** for bookings under 6 hours")

elif selected_page == "Bookings":
    st.title("Bookings")

    # Add a new booking
    st.header("Add a New Booking")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    preferred_date = st.date_input("Preferred Date")
    preferred_time = st.time_input("Preferred Time")
    service_type = st.selectbox("Service Type", ["Coffee Catering", "Event Barista", "Temporary Staff"])
    add_ons = st.text_area("Add-ons")

    if st.button("Add Booking"):
        # Here, you would call a function like add_booking() to insert the booking into the database
        st.success("Booking added successfully!")

