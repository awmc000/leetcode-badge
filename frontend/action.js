function isAlphaNumeric(str) {
    var code, i, len;
  
    for (i = 0, len = str.length; i < len; i++) {
        code = str.charCodeAt(i);
        if (!(code > 47 && code < 58) && // numeric (0-9)
            !(code > 64 && code < 91) && // upper alpha (A-Z)
            !(code > 96 && code < 123)) { // lower alpha (a-z)
        return false;
      }
    }
    return true;
};

async function submitUsername() {
    var formData = new FormData(document.forms[0])

    var obj = Object.fromEntries(Array.from(formData.keys())
        .map(key => [key, formData.getAll(key).length > 1 ?
            formData.getAll(key) : formData.get(key)]));

    var jsonreq = (`${JSON.stringify(obj)}`);

    if (!isAlphaNumeric(obj.username)) {
        window.alert("Enter a username containing letters and numbers only.");
        document.getElementById("submit-btn").disabled = false;
        return;
    }

    const response = await fetch('https://leetcode-badge-eight.vercel.app', {
        method: "POST",
        body: jsonreq,
        headers: {"Content-type": "application/json; charset=UTF-8"}
    }) 
        .catch(error => console.log(error))
        .then(r => r.blob())
        .then(blobFile => 
            new File([blobFile], "lcbadge.png", { type: "image/png"}));

    const url = URL.createObjectURL(response);

    document.getElementById("badgeImage").src=url;
    document.getElementById("submit-btn").disabled = false;
    console.log(response);
}

async function submitUsernameChart() {
    var formData = new FormData(document.forms[0])

    var obj = Object.fromEntries(Array.from(formData.keys())
        .map(key => [key, formData.getAll(key).length > 1 ?
            formData.getAll(key) : formData.get(key)]));

    var jsonreq = (`${JSON.stringify(obj)}`);

    if (!isAlphaNumeric(obj.username)) {
        window.alert("Enter a username containing letters and numbers only.");
        document.getElementById("submit-btn").disabled = false;
        return;
    }

    const response = await fetch('https://leetcode-badge-eight.vercel.app/pie', {
        method: "POST",
        body: jsonreq,
        headers: {"Content-type": "application/json; charset=UTF-8"}
    }) 
        .catch(error => console.log(error))
        .then(r => r.blob())
        .then(blobFile => 
            new File([blobFile], "lcchart.png", { type: "image/png"}));

    const url = URL.createObjectURL(response);

    document.getElementById("chartImage").src=url;
    document.getElementById("chartImage").style.width = '278px';
    document.getElementById("chartImage").style.height = '234px';
    document.getElementById("submit-btn2").disabled = false;
    console.log(response);
}