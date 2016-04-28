# Express-backend
Express-backend V0.0.8:

done:1.Qrcode 2.random string with 10 characters 3.fix JsonResponse 4.save the receiver's data into database

todo:1.optimize the code 2.public server deploy 3.todos in the code

APIS:

step 1:

request:localhost:8000/express/?name=...&address=...&phone=...

response:Url(point to the html),code

request:localhost:8000/express/?code=....

response:html(with Qrcode)

step 3:

request:localhost:8000/sending/?code=...&pos=...&deliverPhone=...

response:feedback(string)

request:localhost:8000/find/?rcvName=...&rcvPhone=...&code=...

response:pos(string)

step 4:

request:localhost:8000/distribute/?code=...&deliverPhone=...

response:feedback(string) message(containing rcvName goods rcvAddress code)

