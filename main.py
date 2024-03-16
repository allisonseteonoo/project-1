import shutil
import sqlite3
import random
import os

from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import SlideTransition

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen

from kivymd.uix.list import MDList
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout

from twilio.rest import Client
from datetime import date, datetime, timedelta

Window.size = (400, 780)

account_sid = 'ACcda1f4c7d57f0c3a0c12defa9fc39d33'
auth_token = 'f8d9a4c1409dfbd6a70d6199d38c4ede'
twilio_phone_number = '+14155238886'
client = Client(account_sid, auth_token)
class MyScrollView(MDScrollView):
    drink_title = StringProperty(" ")

    def __init__(self, **kwargs):
        super(MyScrollView, self).__init__(**kwargs)
        self.do_scroll_x: False
        self.do_scroll_y: True

        # create kivy boxlayout to place buttons and labels inside
        self.layout_box = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            size_hint_x=1,
            id="layout_box"
        )

        self.add_widget(self.layout_box)
        # adjusting height of layout_box to change according to number of buttons and labels inside
        self.layout_box.bind(minimum_height=self.layout_box.setter('height'))

        self.buttons = []
        self.add_buttons()

    def on_button_release(self, button):
        pass
    def button_pressed_callback(self, button):
        if button in self.buttons:
            index = self.buttons.index(button)
            self.buttons[index].state = button.state
    def add_buttons(self):
        self.buttons.clear()

        conn = sqlite3.connect("wisdomcafe.db")
        c = conn.cursor()

        # fetch specifications of the drink chosen
        c.execute("SELECT ice, syrup FROM menu WHERE drink_name = ?", (self.drink_title, ))
        selection = c.fetchone()

        if selection:
            ice, syrup = selection
            if ice == 1:
                self.add_ice_buttons()
            if syrup == 1:
                self.add_syrup_buttons()

        conn.close()

    def add_ice_buttons(self):
        ice_label = MyLabel(
            text='Ice',
            font_size=30,
            color=[0, 0, 0, 1],  # Black color in RGBA
            pos_hint={"center_x": 0.5},
            font_name="Fonts/Nexa-Heavy.ttf",
            size_hint_y=None,
            height=60
        )
        self.layout_box.add_widget(ice_label)
        no_ice_button = self.add_menu_button("ice", "No Ice", "option_button1")
        no_ice_button.state = 'down'
        self.add_menu_button("ice", "Half Ice", "option_button2")
        self.add_menu_button("ice", "Full Ice", "option_button3")

    def add_syrup_buttons(self):
        syrup_label = MyLabel(
            text='Syrup',
            font_size=30,
            color=[0, 0, 0, 1],
            pos_hint={"center_x": 0.5},
            size_hint_y=None,
            height=60,
            font_name="Fonts/Nexa-Heavy.ttf"
        )
        self.layout_box.add_widget(syrup_label)
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # Fetch syrup names from the database
        c.execute("SELECT syrup_name FROM syrups")
        syrup_names = c.fetchall()

        for index, syrup_name in enumerate(syrup_names):
            button_id = f"option_button{index + 4}"  # Assuming index starts from 0
            self.add_menu_button("syrup", syrup_name[0], button_id)

        conn.close()

    def add_menu_button(self, group_name, button_text, button_id):
        button = MenuButton(
            group=group_name,
            text=button_text,
            id=button_id,
        )
        button.bind(on_release=self.on_button_release)
        button.bind(on_press=self.button_pressed_callback)
        self.buttons.append(button)
        self.layout_box.add_widget(button)
        return button

    def untoggle_all_buttons(self):
        for button in self.buttons:
            button.state = 'normal'

    def update_layout(self):
        self.drink_title = App.get_running_app().drinkTitle
        self.layout_box.clear_widgets()
        self.layout_box.bind(minimum_height=self.layout_box.setter('height'))
        self.add_buttons()

    def get_selected_values(self):
        selected_ice = ""
        selected_syrup = ""

        for button in self.buttons:
            if button.state == "down":
                if button.group == "ice":
                    selected_ice = button.text
                elif button.group == "syrup":
                    selected_syrup = button.text

        app_instance = App.get_running_app()
        app_instance.receive_selected_values(selected_ice, selected_syrup)

class CafeList(MDList,MDGridLayout):
    def __init__(self, **kwargs):
        super(MDList, self).__init__(**kwargs)
        self.row_default_height = "150"

class Cashier(MDScreen):
    pass

class OrderInfo(MDScreen):
    pass

class RecapOrder(MDScreen):
    pass

class OrderList(MDList):
    pass

class CartModifiedList(MDList):
    def __init__(self, **kwargs):
        super(CartModifiedList, self).__init__(**kwargs)
        self.data = [{'text': f'Order {i}'} for i in range(5)]  # Example data

    def on_children(self, instance, value):
        total_height = sum(child.height for child in value)
        self.height = total_height + (len(value) - 1) * self.spacing[1]

class CartList(MDList):
    def __init__(self, **kwargs):
        super(MDList, self).__init__(**kwargs)
        self.row_default_height = "180"
    def add_new_multiline_icon_float(self,drink,ice,syrup,value):
        new_multiline_icon_float = MultiLineFloatLayout()
        new_multiline_icon_float.set_label_texts(drink,ice,syrup,value)
        self.add_widget(new_multiline_icon_float)

class DrinkList(MDList):
    def __init__(self, **kwargs):
        super(MDList, self).__init__(**kwargs)
        self.row_default_height = "180"

class IcedDrinks(MDScreen):
    pass

class HotDrinks(MDScreen):
    pass

class ManualDrinks(MDScreen):
    pass

class EditDrink(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
        self.image_url = None

    @staticmethod
    def move_file_to_folder(source_path, destination_folder):
        # Path to the destination folder within your Python project directory
        destination_path = os.path.join(destination_folder, os.path.basename(source_path))
        # Move the file to the destination folder
        shutil.move(source_path, destination_path)

    def upload_image(self,instance):
        # Open file chooser dialog for image selection
        file_chooser = FileChooserIconView()
        file_chooser.bind(on_submit=self.save_image_link)
        self.popup = Popup(title="Select Image", content=file_chooser, size_hint=(0.7, 0.7))
        self.popup.open()

    def save_image_link(self, instance, selection, *args):
        if selection:
            selected_file = selection[0]
            self.image_url = selected_file
            self.image_link = selected_file.split('/')[-1]

            # Close the file chooser dialog
            self.popup.dismiss()

    def save_options(self):
        if self.image_url:
            self.move_file_to_folder(self.image_url, "images")
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        new_ice_state = 0

        if self.ids.ice_toggle.state == "down":
            new_ice_state = 1

        new_syrup_state = 0

        if self.ids.syrup_toggle.state == "down":
            new_syrup_state = 1

        post_state = " "

        if self.ids.check_iced.state == "down":
            post_state = "Iced"
        elif self.ids.check_hot.state == "down":
            post_state = "Hot"
        elif self.ids.check_manual.state == "down":
            post_state = "Manual"

        # check if drink exists in database
        c.execute("SELECT drink_name FROM menu WHERE drink_name = ?", (self.ids['name_field'].text,))
        existing_row = c.fetchone()
        # if exists, update menu with inputted options
        if existing_row:
            c.execute("""
                    UPDATE menu 
                    SET drink_desc = ?, ice = ?, syrup = ?, post = ?, image = ?
                    WHERE drink_name = ?
                """, (
            self.ids['desc_field'].text, new_ice_state, new_syrup_state, post_state, f"images/{self.image_link}", self.ids['name_field'].text,))
        # if not exists, add to menu with inputted options
        else:
            c.execute("""
                    INSERT INTO menu 
                    (drink_name, drink_desc, ice, syrup, post, image) 
                    VALUES (?,?,?,?,?,?)
                """, (
            self.ids['name_field'].text, self.ids['desc_field'].text, new_ice_state, new_syrup_state, post_state, f"images/{self.image_link}",))

        conn.commit()
        conn.close()

        app = App.get_running_app()
        app.generate_menu()
        app.generate_edit_menu()
class SelectMenuButton(MDFloatLayout):
    def on_add_to_cart(self):
        if not self.ids.add_to_cart.disabled:
            app = App.get_running_app()
            app.root.transition.direction = "left"
            app.root.current = "customorderscreen"
            app.replace_text(self.ids.name.text)
            app.replace_desc(self.ids.description.text)
class MyLabel(MDLabel):
    def __init__(self, **kwargs):
        super(MDLabel, self).__init__(**kwargs)
        self.font_name="Fonts/Nexa-Heavy.ttf"
class MenuButton(MDToggleButton, MDRectangleFlatButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = "e9edf5"
        self.font_color_down = "black"
        self.font_color_normal = "black"
        self.background_normal = "white"
        self.allow_no_selection = False

class SyrupButton(MDFloatLayout):
    def delete_syrup_option(self, layout_instance):
        syrup_name = layout_instance.ids.syrup_name.text

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # removing syrup from database
        c.execute("DELETE FROM syrups WHERE syrup_name = ?", (syrup_name,))

        conn.commit()
        conn.close()

        app = App.get_running_app()
        app.generate_syrup_options()
class FullOrderModified(MDFloatLayout):
    def __init__(self, **kwargs):
        super(MDFloatLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.setup_ui, 0)
    def setup_ui(self, dt):
        self.ids.each_order_list.bind(minimum_height=self.update_height)
    def update_height(self, instance, height):
        self.height = self.ids.each_order_list.height + dp(50)
class FullOrder(MDFloatLayout):
    def __init__(self, **kwargs):
        super(MDFloatLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.setup_ui, 0)
    def setup_ui(self, dt):
        self.ids.each_order_list.bind(minimum_height=self.update_height)
    def update_height(self, instance, height):
        self.height = self.ids.each_order_list.height + dp(50)

    def delete_order(self, layout_instance):
        today_date = date.today()

        # Extract order number from the order text
        order_text= layout_instance.ids.order_no.text
        hash_index = order_text.find('#')

        if hash_index != -1:
            number_after_hash = order_text[hash_index + 1:]
            order_no = int(number_after_hash)
        else:
            # Print a message if '#' is not found in the string
            print("No '#' found in the string")

        # Call a method to delete the order from order history
        app_instance = App.get_running_app()
        app_instance.delete_from_order_history(order_text)

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # Mark the order as processed in the database
        c.execute("""
            UPDATE orders 
            SET is_processed = ? 
            WHERE daily_group_order = ? AND order_date = ?
        """, (1, order_no, today_date))

        conn.commit()
        conn.close()

        self.parent.remove_widget(self)

    def send_whatsapp_message(self,layout_instance):
        # fetch date today and order number
        today_date = date.today()
        order_text = layout_instance.ids.order_no.text
        hash_index = order_text.find('#')

        if hash_index != -1:
            number_after_hash = order_text[hash_index + 1:]
            order_no = int(number_after_hash)
        else:
            print("No '#' found in the string")

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # fetch customer phone number based on date today and order number
        c.execute("SELECT customer_id FROM orders WHERE daily_group_order = ?  AND order_date = ?",
                  (order_no, today_date, ))
        result = c.fetchone()

        phone_no_from_db = str(result[0])

        conn.commit()
        conn.close()

        # create message to be sent to customer phone number
        message = client.messages.create(
            from_='whatsapp:{}'.format(twilio_phone_number),
            body=f'Your Order #{order_no} is ready! Please pick up at the counter.',
            to='whatsapp:{}'.format(phone_no_from_db)
        )

        print('WhatsApp message sent. SID:', message.sid)



class VerificationCode(MDFloatLayout):
    def __init__(self, code_sent, passwrd, phone_no, **kwargs):
        super().__init__(**kwargs)
        self.code_sent = code_sent
        self.passwrd = passwrd
        self.phone_no = phone_no

    def verify_code(self):
        code_returned = self.ids.code.text
        if self.code_sent == code_returned:
            app = App.get_running_app()
            app.insert_customer_log(self.phone_no,self.passwrd)
        else:
            error_label = MDLabel(
                text='Invalid code!',
                font_size=20,
                color="red",
                pos_hint={"center_x": 0.5, "center_y": 0.31},
                halign="center",
                size_hint_y=None,
                height=60,
                font_name="Fonts/Nexa-ExtraLight.ttf"
            )

            self.add_widget(error_label)

    def resend_code(self):
        new_six_digit_number = random.randint(100000, 999999)

        verify = client.messages.create(
            from_='whatsapp:{}'.format(twilio_phone_number),
            body=f'{new_six_digit_number}',
            to='whatsapp:{}'.format(self.phone_no)
        )

        # replace code to be checked with new six digit number
        self.code_sent = new_six_digit_number
class Order(MDFloatLayout):
    counter = 0
    def __init__(self, order_no, **kwargs):
        super().__init__(**kwargs)
        self.order_no = order_no
    def set_specs(self, order_no, drink, ice, syrup, amount):
        self.ids.order_no.text = "#" + str(order_no)
        if drink is not None:
            self.ids.drink_spec.text = drink
        if ice is not None:
            self.ids.ice_spec.text = ice
        if syrup is not None:
            self.ids.syrup_spec.text = syrup
        if amount is not None:
            self.ids.count_spec.text = str(amount)

    def delete_layout(self, layout_instance):
        parent_layout = layout_instance.parent
        today_date = date.today()
        order_text = layout_instance.ids.order_no.text
        hash_index = order_text.find('#')
        if hash_index != -1:
            number_after_hash = order_text[hash_index + 1:]
            order_num = int(number_after_hash)

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        c.execute("UPDATE orders SET is_created = ? WHERE daily_group_order = ?  AND order_date = ? AND order_no = ?",
                  (1, order_num, today_date, self.order_no))

        conn.commit()
        conn.close()

        parent_layout.remove_widget(layout_instance)

class EditMenuButton(MDFloatLayout):
    def __init__(self, **kwargs):
        super(MDFloatLayout, self).__init__(**kwargs)
        self.checkbox_state = False

    def toggle_checkbox(self, layout_instance):
        drink_name = layout_instance.ids.name.text

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        if self.ids.check_status.icon == "checkbox-blank-outline":
            c.execute("UPDATE menu SET sold_out = ? WHERE drink_name = ?", (1, drink_name, ))
        else:
            c.execute("UPDATE menu SET sold_out = ? WHERE drink_name = ?", (0, drink_name,))

        conn.commit()
        conn.close()

        app = App.get_running_app()
        app.generate_edit_menu()
        app.generate_menu()

    def delete_menu_option(self, layout_instance):
        drink_name = layout_instance.ids.name.text

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        c.execute("DELETE FROM menu WHERE drink_name = ?", (drink_name,))

        conn.commit()
        conn.close()

        app = App.get_running_app()
        app.generate_edit_menu()
        app.generate_menu()

class EditMenu(MDScreen):
    pass

class EditSyrup(MDScreen):
    def add_new_syrup(self):
        # fetch name of syrup from text field
        new_syrup = self.ids.syrup_name.text

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # check if syrup exists
        c.execute("SELECT * FROM syrups WHERE syrup_name = ?", (new_syrup,))
        existing_syrup = c.fetchone()

        if existing_syrup:
            print(f"{new_syrup} already exists in the database.")
        else:
            # add into database if it does not exist yet
            c.execute("INSERT INTO syrups (syrup_name) VALUES (?)", (new_syrup,))
            conn.commit()
            print(f"{new_syrup} added to the database.")

        self.ids.syrup_name.text = " "

        app = App.get_running_app()
        app.generate_syrup_options()

        conn.close()
class MultiLineFloatLayout(MDFloatLayout):
    number_id = 1
    def set_label_texts(self,drink_type, ice_type,syrup_type,amount):
        self.ids.drink_text.text = drink_type
        self.ids.ice_text.text = ice_type
        self.ids.syrup_text.text = syrup_type
        self.number_id = amount
        self.ids.count_text.text = str(self.number_id)

        if drink_type == 'Hot Latte':
            self.ids.syrup_text.pos_hint = {"center_x":0.55,"center_y":0.50}

    def add(self, layout_instance):
        layout_instance.number_id += 1
        layout_instance.ids.count_text.text = str(layout_instance.number_id)

    def subtract(self, layout_instance):
        parent_layout = layout_instance.parent
        layout_instance.number_id -= 1
        layout_instance.ids.count_text.text = str(layout_instance.number_id)
        if layout_instance.number_id == 0:
            parent_layout.remove_widget(layout_instance)


class MainMenuScreen(MDScreen):
    pass

class CustomerSignupScreen(MDScreen):
    def send_verification_code(self, phone_number, pass_word):
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        c.execute("SELECT * from customer_log WHERE phone_number = ?",
                  (phone_number, ))
        result = c.fetchone()

        conn.close()

        app = App.get_running_app()
        screen = app.root.get_screen('customersignupscreen')

        if result:
            error_label = MDLabel(
                text='Number already exists!',
                font_size=20,
                color="red",
                pos_hint={"center_x": 0.5, "center_y": 0.29},
                halign="center",
                size_hint_y=None,
                height=60,
                font_name="Fonts/Nexa-ExtraLight.ttf",
                id="number_exists"
            )
            screen.add_widget(error_label)
        else:
            password_text = self.ids.passwrd.text.strip()
            if password_text:
                # create random six-digit number
                six_digit_number = random.randint(100000, 999999)

                # display verification code screen
                ver_code = VerificationCode(code_sent=str(six_digit_number), passwrd=pass_word, phone_no=phone_number,)
                ver_code.ids.title.text = f"Please enter the verification code sent to {phone_number}"
                self.add_widget(ver_code)
                identification_text = self.ids.identification.text

                # send random six digit number
                verify = client.messages.create(
                    from_='whatsapp:{}'.format(twilio_phone_number),
                    body=f'{six_digit_number}',
                    to='whatsapp:{}'.format(identification_text)
                )
            else:
                error_label = MDLabel(
                    text='No password entered!',
                    font_size=20,
                    color="red",
                    pos_hint={"center_x": 0.5, "center_y": 0.29},
                    halign="center",
                    size_hint_y=None,
                    height=60,
                    font_name="Fonts/Nexa-ExtraLight.ttf"
                )
                screen.add_widget(error_label)
    def resetForm(self):
        self.ids.identification.text = ""
        self.ids.passwrd.text = ""

class WorkerLoginScreen(MDScreen):
    def do_login(self, loginText, passwordText):
        if loginText == "mother" and passwordText == "teresa":
            self.manager.transition = SlideTransition(direction="left")
            app = App.get_running_app()
            app.root.current = "workermenuscreen"
            self.resetForm()
        else:
            error_label = MDLabel(
                text='ERROR!',
                font_size=20,
                color="red",
                pos_hint={"center_x": 0.5,"center_y": 0.29},
                halign= "center",
                size_hint_y=None,
                height=60,
                font_name="Fonts/Nexa-ExtraLight.ttf"
            )

            self.add_widget(error_label)

    def resetForm(self):
        self.ids['identification'].text = ""
        self.ids['passwrd'].text = ""

class WorkerMenuScreen(MDScreen):
    pass

class WindowManager(MDScreenManager):
    pass
class OrderModified(MDFloatLayout):
    pass

class CustomerMenuScreen(MDScreen):
    pass

class CustomerLoginScreen(MDScreen):
    def do_login(self, loginText, passwordText):
        if loginText == "" and passwordText == "":
            self.manager.transition = SlideTransition(direction="left")
            app = App.get_running_app()
            app.root.current = "customermenuscreen"
            self.resetForm()
        else:
            error_label = MDLabel(
                text='ERROR!',
                font_size=20,
                color="red",
                pos_hint={"center_x": 0.5,"center_y": 0.29},
                halign= "center",
                size_hint_y=None,
                height=60,
                font_name="Fonts/Nexa-ExtraLight.ttf"
            )

            self.add_widget(error_label)
    def resetForm(self):
        self.ids['identification'].text = ""
        self.ids['passwrd'].text = ""

class CartScreen(MDScreen):
    def cancel_order(self):
        cart_list = self.ids.cartlist
        cart_list.clear_widgets()

class CustomOrderScreen(MDScreen):
    pass
class WisdomCafeApp(MDApp):
    customer_no = " "

    def build(self):
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id TEXT,
                        drink_title TEXT,
                        ice TEXT,
                        syrup TEXT,
                        amount INTEGER,
                        is_created INTEGER,
                        is_processed INTEGER,
                        order_date DATE,
                        order_no INTEGER,
                        daily_group_order INTEGER DEFAULT 1  -- New column for daily group order number
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS customer_log (
                                phone_number TEXT UNIQUE,
                                password TEXT
                            )""")
        c.execute("""CREATE TABLE IF NOT EXISTS menu (
                                        drink_name TEXT UNIQUE,
                                        drink_desc TEXT, 
                                        ice INTEGER,
                                        syrup INTEGER,
                                        post TEXT,
                                        sold_out INTEGER DEFAULT 0,
                                        image TEXT
                                    )""")
        c.execute("CREATE TABLE IF NOT EXISTS syrups (syrup_name TEXT UNIQUE)")
        c.execute("""
                            UPDATE menu 
                            SET image = ?
                            WHERE drink_name = ?
                        """, ('images/iced-v60-pic.jpeg','Japanese V60', ))

        c.execute("SELECT * FROM menu")
        rows = c.fetchall()
        for row in rows:
            print(row)

        conn.commit()
        conn.close()
        return Builder.load_file('wisdomcafe.kv')

    def on_start(self):
        Clock.schedule_interval(self.periodic_update, 10)
        # Sets all screens that contain orders in application
        self.generate_order_history()
        self.generate_full_orders()
        self.current_order()
        self.generate_menu()
        self.generate_edit_menu()
        self.generate_syrup_options()
    def periodic_update(self, dt):
        # Resets the screens with dynamic orders
        self.generate_full_orders()
        self.generate_order_history()
        self.current_order()

    def insert_customer_log(self, phone_number, password):
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        c.execute("INSERT INTO customer_log (phone_number, password) VALUES (?, ?)",
                      (phone_number, password))

        print("Customer log inserted successfully!")

        c.execute(f"SELECT * FROM customer_log;")
        rows = c.fetchall()

        if not rows:
            print("Table is empty.")
        else:
            print(f"Contents of customer_log:")
            for row in rows:
                print(row)

        conn.commit()

        self.root.get_screen('customersignupscreen').resetForm()
        self.root.get_screen('customersignupscreen').manager.transition = SlideTransition(direction="left")
        app = App.get_running_app()
        app.root.current = "customermenuscreen"

        conn.close()

        self.customer_no = phone_number

    def check_login_credentials(self, phone_number, password):
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        c.execute("""
            SELECT * 
            FROM customer_log 
            WHERE phone_number = ? 
            AND password = ?
        """, (phone_number, password,))
        result = c.fetchone()

        if result is not None:
            phone_no, passwrd = result
            self.customer_no = phone_no
            self.root.get_screen('customerloginscreen').manager.transition = SlideTransition(direction="left")
            app = App.get_running_app()
            app.root.current = "customermenuscreen"
            self.root.get_screen('customerloginscreen').resetForm()
        else:
            error_label = MDLabel(
                text='Password or number is invalid',
                font_size=20,
                color="red",
                pos_hint={"center_x": 0.5, "center_y": 0.29},
                halign="center",
                size_hint_y=None,
                height=60,
                font_name="Fonts/Nexa-ExtraLight.ttf"
            )

            self.root.get_screen('customerloginscreen').add_widget(error_label)

        conn.close()
    def current_order(self):
        order_info_screen = self.root.get_screen('orderinfoscreen')

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        c.execute("""
            SELECT daily_group_order
            FROM orders
            WHERE order_date = ? AND is_processed = 0
            ORDER BY daily_group_order
            LIMIT 1
        """, (date.today(),))
        ongoing_order = c.fetchone()

        if ongoing_order is None:
            order_info_screen.ids.ongoing_order_number.text = "NONE"
        else:
            ongoing_order_no = str(ongoing_order[0])
            order_info_screen.ids.ongoing_order_number.text = f'ORDER #{ongoing_order_no}'

        conn.close()

    def date_with_highest_orders(self):
        recap_order_screen = self.root.get_screen('recaporderscreen')
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # Get the first day of the current month
        current_month_first_day = datetime.now().replace(day=1)

        # Get the last day of the current month
        next_month_first_day = current_month_first_day.replace(month=current_month_first_day.month + 1)
        current_month_last_day = next_month_first_day - timedelta(days=1)

        # Finding the date within the current month with the highest total number of orders
        c.execute("""
                SELECT order_date, SUM(amount) as total_drinks
                FROM orders
                WHERE is_processed = 1
                AND order_date >= ? AND order_date <= ?
                GROUP BY order_date
                ORDER BY total_drinks DESC
                LIMIT 1
            """, (current_month_first_day, current_month_last_day))

        result = c.fetchone()

        if result:
            highest_orders_date, total_orders = result
            recap_order_screen.ids.monthly_highest.text = str(total_orders)

        conn.close()

    def return_total_order(self):
        recap_order_screen = self.root.get_screen('recaporderscreen')

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # counting the total number of orders in that date
        c.execute("""
                SELECT SUM(amount) as total_orders
                FROM orders
                WHERE order_date = ? AND is_processed = 1
            """, (date.today(),))

        result = c.fetchone()

        if result:
            total_orders = result[0]
            recap_order_screen.ids.weekly_total.text = str(total_orders)

        conn.close()

    def current_recap(self):
        recap_order_screen = self.root.get_screen('recaporderscreen')

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # selecting the drink that is the most ordered by adding the sum of the amount per order
        c.execute("""
                SELECT drink_title, SUM(amount) AS order_count
                FROM orders
                WHERE order_date = ? AND is_processed = 1  -- Assuming is_processed = 1 for processed orders
                GROUP BY drink_title
                ORDER BY order_count DESC
                LIMIT 1
            """, (date.today(),))

        result = c.fetchone()

        if result:
            most_ordered_drink, order_count = result
            recap_order_screen.ids.top_drink.text = str(most_ordered_drink)
            recap_order_screen.ids.top_drink_no.text = str(order_count)
            if order_count == 1:
                recap_order_screen.ids.drink_order_label.text = 'Order'

        conn.close()

    def current_recap_syrup(self):
        recap_order_screen = self.root.get_screen('recaporderscreen')

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # selecting the syrup that is the most ordered by adding the sum of the amount per order
        c.execute("""
            SELECT syrup, COUNT(syrup) AS syrup_count
            FROM orders
            WHERE order_date = ? AND is_processed = 1 AND syrup IS NOT NULL AND syrup != ''
            GROUP BY syrup
            ORDER BY syrup_count DESC
            LIMIT 1
        """, (date.today(),))

        result = c.fetchone()

        if result:
            most_ordered_syrup, syrup_count = result
            recap_order_screen.ids.top_syrup.text = str(most_ordered_syrup)
            recap_order_screen.ids.top_syrup_no.text = str(syrup_count)
            if syrup_count == 1:
                recap_order_screen.ids.syrup_order_label.text = 'Order'

        conn.close()

    def set_options(self, name, desc):
        edit_drink_menu = self.root.get_screen('editdrinkscreen')

        # displaying drink name and description in text field
        edit_drink_menu.ids.name_field.text = name
        edit_drink_menu.ids.name_field.readonly = True
        edit_drink_menu.ids.desc_field.text = desc

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # accessing drink properties from table based on drink name fetched
        c.execute("SELECT ice, syrup, post FROM menu WHERE drink_name =?", (name, ))
        rows = c.fetchall()

        # displaying drink properties with buttons
        for row in rows:
            ice, syrup, post = row
            if ice == 1:
                edit_drink_menu.ids.ice_toggle.state = "down"
            if syrup == 1:
                edit_drink_menu.ids.syrup_toggle.state = "down"
            if post == 'Iced':
                edit_drink_menu.ids.check_iced.state = "down"
            elif post == 'Hot':
                edit_drink_menu.ids.check_hot.state = "down"
            elif post == 'Manual':
                edit_drink_menu.ids.check_manual.state = "down"

            conn.close()

    drinkTitle = StringProperty("")

    def reset_toggle_options(self):
        edit_drink_menu = self.root.get_screen('editdrinkscreen')
        edit_drink_menu.ids.name_field.readonly = False
        edit_drink_menu.ids.name_field.text = " "
        edit_drink_menu.ids.desc_field.text = " "
        edit_drink_menu.ids.ice_toggle.state = "normal"
        edit_drink_menu.ids.syrup_toggle.state = "normal"
        edit_drink_menu.ids.check_iced.state = "normal"
        edit_drink_menu.ids.check_hot.state = "normal"
        edit_drink_menu.ids.check_manual.state = "normal"

    def replace_text(self, text):
        setattr(self, 'drinkTitle', text)
        scroll_view = self.root.get_screen('customorderscreen').ids.scrollview_customer
        scroll_view.update_layout()

    drinkDesc = StringProperty("")

    def replace_desc(self, text):
        self.drinkDesc = text

    guestName = StringProperty("Name of Customer")

    def replace_name(self,text):
        self.guestName = text
    def untoggle_all_buttons(self):
        scroll_view = self.root.get_screen(
            'customorderscreen').ids.scrollview_customer  # Replace 'screen_name' and 'scroll_view_id'
        scroll_view.untoggle_all_buttons()

    counter = StringProperty("1")
    count = 1

    def plus(self):
        self.count = self.count + 1
        self.counter = str(self.count)

    def minus(self):
        if self.count != 1:
            self.count = self.count - 1
            self.counter = str(self.count)

    stored_count = 1

    def reset_order(self):
        self.counter = "1"
        self.count = 1

    def place_order(self):
        self.stored_count = self.count
        options = self.root.get_screen(
            'customorderscreen').ids.scrollview_customer
        options.get_selected_values()

    def check_text_length(self, text_field, new_text):
        max_length = 6
        if len(new_text) > max_length:
            text_field.text = new_text[:max_length]

    def receive_selected_values(self,ice_value,syrup_value):
        cafe_list_screen = self.root.get_screen('cartscreen').ids.cartlist  # Replace with actual ID used in your app
        cafe_list_screen.add_new_multiline_icon_float(self.drinkTitle, ice_value, syrup_value, self.stored_count)

    def place_order_to_database(self):
        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        cart_list = self.root.get_screen('cartscreen').ids.cartlist

        # fetching the highest integer in daily_group_order for the date today
        c.execute("""
                SELECT MAX(daily_group_order) FROM orders WHERE order_date = ?
            """, (date.today(),))
        max_group_order = c.fetchone()[0]

        # making the next number one more than the highest integer
        next_group_order = max_group_order + 1 if max_group_order else 1

        # default to 0; in order to give each drink inside an order distinction
        order_number = 0

        # loop fetching the content of the list of drinks in customer's cart to input into database
        for child in cart_list.children:
            if isinstance(child, MultiLineFloatLayout):
                drink = child.ids.drink_text.text
                ice = child.ids.ice_text.text
                syrup = child.ids.syrup_text.text
                amount = child.ids.count_text.text
                order_number += 1
                c.execute("""
                    INSERT INTO orders 
                    (customer_id, drink_title, ice, syrup, amount, order_date, daily_group_order, order_no) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.customer_no, drink, ice, syrup, amount, date.today(), next_group_order, order_number))

        c.execute(f"SELECT * FROM orders;")
        rows = c.fetchall()

        if not rows:
            print("Table is empty.")
        else:
            print(f"Contents of table orders:")
            for row in rows:
                print(row)

        conn.commit()
        conn.close()
    def generate_menu(self):
        main_menu = self.root.get_screen('customermenuscreen').ids.menulist
        main_menu.clear_widgets()

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        # selecting all drink names and corresponding description from menu table
        c.execute("SELECT drink_name, drink_desc, image, sold_out FROM menu")
        menu_items = c.fetchall()

        # creating a widget which displays the drink name and description on the menu screen
        for item in menu_items:
            drink_name, drink_desc, image, sold_out = item
            menu_display = SelectMenuButton()
            menu_display.ids.name.text = drink_name
            menu_display.ids.description.text = drink_desc
            if sold_out == 1:
                menu_display.ids.add_to_cart.disabled = True
            if image is not None:
                menu_display.ids.drink_image.source = image
            main_menu.add_widget(menu_display)

        conn.close()

    def generate_syrup_options(self):
        # access list to place widgets
        syrup_list = self.root.get_screen('editsyrupscreen').ids.syruplist
        syrup_list.clear_widgets()

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # fetch all syrup names from syrups table
        c.execute("SELECT syrup_name FROM syrups")
        menu_items = c.fetchall()

        # loop creating widgets of each syrup name to place into list
        for item in menu_items:
            syrup_name = item[0]
            syrup_button = SyrupButton()
            syrup_button.ids.syrup_name.text = syrup_name
            syrup_list.add_widget(syrup_button)

        conn.close()
    def generate_edit_menu(self):
        edit_menu = self.root.get_screen('editmenuscreen').ids.editmenulist
        edit_menu.clear_widgets()

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        c.execute("SELECT drink_name, drink_desc, image, sold_out FROM menu")
        menu_items = c.fetchall()
        # create a widget which displays drink name and description for workers to edit
        for item in menu_items:
            drink_name, drink_desc, image, sold_out = item
            menu_display = EditMenuButton()
            menu_display.ids.name.text = drink_name
            menu_display.ids.description.text = drink_desc
            if sold_out == 1:
                menu_display.ids.check_status.icon = "checkbox-marked"
            if image is not None:
                menu_display.ids.drink_image.source = image
            edit_menu.add_widget(menu_display)

        conn.close()
    def generate_full_orders(self):
        # accessing the screens for individual orders
        iced_orders_screen = self.root.get_screen('icedorderscreen').ids.icedorderlist
        hot_orders_screen = self.root.get_screen('hotorderscreen').ids.hotorderlist
        manual_orders_screen = self.root.get_screen('manualorderscreen').ids.manualorderlist

        # clearing the current widgets inside the screen to avoid overlap
        iced_orders_screen.clear_widgets()
        hot_orders_screen.clear_widgets()
        manual_orders_screen.clear_widgets()

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()

        # selecting all orders from orders table which have not been processed and was created today
        c.execute("""
            SELECT drink_title, ice, syrup, amount, daily_group_order, is_created, order_no
            FROM orders
            WHERE order_date = ? AND is_processed = 0
        """, (date.today(),))

        orders = c.fetchall()

        # looping the creation of widgets for each order selected from the database
        for order in orders:
            drink_title, ice, syrup, amount, daily_group_order, is_created, order_no = order
            new_order = Order(order_no)
            new_order.set_specs(daily_group_order,drink_title,ice,syrup,amount)
            # only adding the widget if they have not been completed by the barista in charge
            if is_created == 0:
                c.execute("SELECT post FROM menu WHERE drink_name = ?", (drink_title, ))
                post = c.fetchone()
                if post:
                    post = post[0]
                    if post == "Iced":
                        iced_orders_screen.add_widget(new_order)
                    if post == "Hot":
                        hot_orders_screen.add_widget(new_order)
                    if post == "Manual":
                        manual_orders_screen.add_widget(new_order)

        # placing drink orders into a new array based on daily_group_order
        grouped_orders = {}
        for order in orders:
            drink_title, ice, syrup, amount, daily_group_order, is_created, order_no = order
            if daily_group_order not in grouped_orders:
                grouped_orders[daily_group_order] = []

            grouped_orders[daily_group_order].append({
                'drink_title': drink_title,
                'ice': ice,
                'syrup': syrup,
                'amount': amount
            })

        conn.close()

        # accessing the cashier's screen and deleting widgets
        cashier_screen = self.root.get_screen('cashierscreen')
        cashier_screen.ids.allorderlist.clear_widgets()

        # looping the creation of widgets for a customer's full order
        for group_order, order_items in grouped_orders.items():
            full_order = FullOrder()
            full_order.ids.order_no.text = f'ORDER #{group_order}'
            each_order_list = full_order.ids.each_order_list

            for order_item in order_items:
                drink_title = order_item['drink_title']
                ice = order_item['ice']
                syrup = order_item['syrup']
                amount = order_item['amount']

                order_modified = OrderModified()
                order_modified.ids.drink_spec.text = drink_title
                order_modified.ids.ice_spec.text = ice
                order_modified.ids.syrup_spec.text = syrup
                order_modified.ids.amount_spec.text = str(amount)
                if drink_title == "Hot Latte":
                    order_modified.ids.syrup_spec.pos_hint = {"center_x":0.55,"center_y":0.50}

                each_order_list.add_widget(order_modified)

            cashier_screen.ids.allorderlist.add_widget(full_order)

    def generate_order_history(self):
        order_info_screen = self.root.get_screen('orderinfoscreen')
        order_info_screen.ids.orderhistorylist.clear_widgets()

        conn = sqlite3.connect('wisdomcafe.db')
        c = conn.cursor()
        c.execute("""
            SELECT drink_title, ice, syrup, amount, daily_group_order
            FROM orders
            WHERE order_date = ? AND is_processed = 0 AND customer_id = ?
        """, (date.today(), self.customer_no,))

        orders = c.fetchall()

        grouped_orders = {}
        for order in orders:
            drink_title, ice, syrup, amount, daily_group_order = order
            if daily_group_order not in grouped_orders:
                grouped_orders[daily_group_order] = []

            grouped_orders[daily_group_order].append({
                'drink_title': drink_title,
                'ice': ice,
                'syrup': syrup,
                'amount': amount
            })

        conn.close()

        for group_order, order_items in grouped_orders.items():
            full_order = FullOrderModified()
            full_order.ids.order_no.text = f'ORDER #{group_order}'
            each_order_list = full_order.ids.each_order_list

            for order_item in order_items:
                drink_title = order_item['drink_title']
                ice = order_item['ice']
                syrup = order_item['syrup']
                amount = order_item['amount']

                order_modified = OrderModified()
                order_modified.ids.drink_spec.text = drink_title
                order_modified.ids.ice_spec.text = ice
                order_modified.ids.syrup_spec.text = syrup
                order_modified.ids.amount_spec.text = str(amount)
                if drink_title == "Hot Latte":
                    order_modified.ids.syrup_spec.pos_hint = {"center_x":0.55,"center_y":0.50}

                each_order_list.add_widget(order_modified)

            order_info_screen.ids.orderhistorylist.add_widget(full_order)
    def delete_from_order_history(self, order_number):
        order_history_list = self.root.get_screen('orderinfoscreen').ids.orderhistorylist

        for child in order_history_list.children:
            if isinstance(child, MDFloatLayout):
                value = child.ids.order_no.text

                if order_number == value:
                    order_history_list.remove_widget(child)


if __name__ == '__main__':
    app = WisdomCafeApp()
    WisdomCafeApp().run()


