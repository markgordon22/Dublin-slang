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
       // Alert sent if email successful
    function(){
            alert("Your email has been sent :) we will be in contact within the next 24 hours");
            location.reload();
},
        // Alert not sent if email was unsuccessful
    function() {
            alert("Your email was not sent :( please try again!");
            location.reload();
        }
   );
   
