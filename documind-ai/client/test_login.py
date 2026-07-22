from auth import login

phone = input("Phone: ")
password = input("Password: ")

response = login(phone, password)

print(response.status_code)
print(response.text)
