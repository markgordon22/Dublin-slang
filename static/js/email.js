/*function validateForm() {
 if (x == "") {
alert("Name must be filled out");
} else if(y == "") {
alert("last name must be filled out");
} else {
if(z == "") {
alert("email address must be filled out");
}
if(a == ""){
alert("textarea must be filled out")
}
else {
sendMail()
}
}


}*/

function sendMail(event) {
    let params = {
        from_name: "Irish Slang",
        first_name: document.getElementById("fname").value,
        last_name: document.getElementById("lname").value,
        from: "markgordon97@gmail.com",
        to: document.getElementById("emailaddress").value,
        message: document.getElementById("msg").value
    };
   
    emailjs.send("service_4b99rtc","template_nllrsno", params)
   .then(
       // Alert sent if email successful
         
            function (response) {
                console.log("SUCCESS", response);
            elem = document.getElementById("modal1")
            let instance = M.Modal.getInstance(elem);
            instance.open()


            },
            function (error) {
                console.log("FAILED", error);
            }
        );
        event.preventDefault();
}
$('.modal').modal();
document.getElementById("emailform").addEventListener('submit', sendMail);