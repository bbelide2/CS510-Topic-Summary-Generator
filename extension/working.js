var domain = "http://107.23.133.88:8000"

chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    let url = tabs[0].url
    document.getElementById("body").innerHTML = "fetching summary ..."
    console.log("Hello World")
    var s = getSummary(url)
})

function getSummary(url) {
    var container = document.getElementById("body")
    container.innerHTML = "Loading....."
    fetch(domain, {
        method: 'POST',
        body: JSON.stringify({
            "url": url
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then((res) => {
        if (res.status == 500) {
            container.innerHTML = "internal server error 1"
        } else {
            return res.json()
        }
    })
    .then((res) => {
        if (res.status == 200) {
           container.innerHTML = res.result.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1">$1</a>').replace(/\n/g, "<br>");
        } else if (res.status == 400) {
            container.innerHTML = "invalid input!"
        } else{
            // container.innerHTML = res.result.replace(/\n/g, "<br>")
            container.innerHTML = res.result.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1">$1</a>').replace(/\n/g, "<br>");

        }
    })
    .catch((err) => {
        return err
    });
}