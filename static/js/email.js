function sendMail() {
let params = {
        from_name: "Irish Slang",
        first_name: document.getElementById("fname").value,
        last_name: document.getElementById("lname").value,
        from: "markgordon97@gmail.com",
        to: document.getElementById("emailaddress").value,
        message: document.getElementById("msg").value
    };

    emailjs.send("service_4b99rtc","template_nllrsno",params)
   .then(