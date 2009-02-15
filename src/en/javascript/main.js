// http://simonwillison.net/2004/May/26/addLoadEvent/
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}

var xmlhttp = null;

function loadXMLDoc(url) {
    if (window.XMLHttpRequest) {// code for Firefox, Opera, IE7, etc.
        xmlhttp = new XMLHttpRequest();
    } else if (window.ActiveXObject) {// code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (xmlhttp != null) {
        xmlhttp.onreadystatechange = stateChange;
        xmlhttp.open("GET",url,true);
        xmlhttp.send(null);
    } else {
        alert("Your browser does not support XMLHTTP.");
    }
}

function stateChange() {
    if (xmlhttp.readyState==4) {// 4 = "loaded"
        document.getElementById('replace').innerHTML = xmlhttp.responseText;
    }
}

addLoadEvent(function () {
    if (navigator.appVersion.indexOf("Win")!=-1) {
        loadXMLDoc("win.html");
    }
});
