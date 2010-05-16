function Download() {
    this.downloads = new Array();
}

Download.prototype = {

    parse_os: function() {
        var OSName="Source code";
        if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
        if (navigator.appVersion.indexOf("Mac")!=-1) {
            if (navigator.userAgent.indexOf("10.6")!=-1 || /* firefox */
                navigator.userAgent.indexOf("10_6") !=-1) { /* chrome */
                OSName="Mac OS X 10.6";
            } else {
                OSName="Mac OS X 10.5";
            }
        }
        if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
        if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";

        return OSName;
    },

    os_detection: function() {
        document.write(this.parse_os());
    },

    os_link: function() {
        var os = this.parse_os();
        if (this.downloads[os]) {
            document.location.href = this.downloads[os];
            return false;
        }
        return true;
    },

    register_download:function(type, url) {
        this.downloads[type] = url;
    }
}
