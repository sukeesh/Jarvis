import pandas as pd

from plugin import plugin


def save(contacts):
    contacts.to_csv('./data/contacts.csv')


@plugin("add contact")
def add_contact(jarvis, s):
    contact_list = pd.read_csv('./data/contacts.csv')
    name = phone = email = carrier = None
    new_contact = dict()

    if s == "":
        name = jarvis.input("Name: ")
        phone = jarvis.input("Phone Number:")
        email = jarvis.input("Email: ")
        carrier = jarvis.input("Phone Network provider: ")

    new_contact['name'] = name
    new_contact['phone'] = phone
    new_contact['email'] = email
    new_contact['carrier'] = carrier
    contact_list.append(new_contact)
    save(contact_list)


@plugin("get contact")
def get_contact(jarvis, s):
    contact_list = pd.read_csv('./data/contacts.csv')
    name = None

    if s == "":
        name = jarvis.input("Name: ")

    print(contact_list[contact_list.name == name])
