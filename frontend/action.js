async function SubmitVars() {
    var formData = new FormData(document.forms[0])

    var obj = Object.fromEntries(Array.from(formData.keys())
        .map(key => [key, formData.getAll(key).length > 1 ?
            formData.getAll(key) : formData.get(key)]));

    var jsonreq = (`${JSON.stringify(obj)}`);

    const response = await fetch('http://127.0.0.1:8000', {
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
    console.log(response);
}