const usernameField=document.querySelector('#usernamefield');
const feedbackArea=document.querySelector('.invalid-feedback');
const emailField=document.querySelector('#emailField');
const emailfeedbackArea=document.querySelector('.emailfeedbackArea');
const passwordfield=document.querySelector('#passwordfield');
const usernameSuccessOutput=document.querySelector('.usernameSuccessOutput');
const ShowPasswordToggle=document.querySelector('.ShowPasswordToggle');
const submitBtn=document.querySelector(".submit-btn")

const handleToggleInput=(e)=> {
    if (ShowPasswordToggle.textContent === 'SHOW') {
        ShowPasswordToggle.textContent = 'HIDE';
        passwordfield.setAttribute('type', 'text');
    } else {
        ShowPasswordToggle.textContent = 'SHOW';
        passwordfield.setAttribute('type', 'password');
    }
};

ShowPasswordToggle.addEventListener('click',handleToggleInput);

emailField.addEventListener('keyup', (e)=>{
const emailVal=e.target.value;
    emailField.style.display='block';
    emailField.textContent=`Checking ${emailVal}`


    emailField.classList.remove('is-invalid');
    emailfeedbackArea.style.display='none';

    if (emailVal.length>0) {
        fetch('/authentication/validate-email', {
            body: JSON.stringify({email: emailVal}),
            method: 'POST',
        })
            .then((res)=>res.json())
            .then((data) => {
                console.log('data',data);
                if (data.email_error){
                    submitBtn.setAttribute('disabled','disabled');
                    submitBtn.disabled = true;
                    emailField.classList.add('is-invalid');
                    emailfeedbackArea.style.display='block';
                    emailfeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
                }else{
                    submitBtn.removeAttribute('disabled');
                }
        });
    }

});


usernameField.addEventListener('keyup', (e) => {


    const usernameVal=e.target.value;
    usernameSuccessOutput.style.display='block';
    usernameSuccessOutput.textContent=`Checking ${usernameVal}`

    usernameField.classList.remove('is-invalid');
    feedbackArea.style.display='none';
    
    if (usernameVal.length>0) {
        fetch('/authentication/validate-username', {
            body: JSON.stringify({username: usernameVal}),
            method: 'POST',
        })
            .then((res)=>res.json())
            .then((data) => {
                usernameSuccessOutput.style.display='none';
                if (data.username_error){
                    usernameField.classList.add('is-invalid');
                    feedbackArea.style.display='block';
                    feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
                    submitBtn.disabled = true;
                }else{
                    submitBtn.removeAttribute('disabled');
                }
        });
    }
});