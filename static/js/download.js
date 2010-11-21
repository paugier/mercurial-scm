function Download (source) {
    this.version = source[0];
    this.regex = source[1];
    this.url = source[2];
    this.desc = source[3];
}

Download.prototype = {
    matches: function (ua) {
        if (ua.match(this.regex))
            return true;
        return false;
    },

    download: function () {
        document.location.href = this.url;
        return false;
    },

    attr: function (key) {
        return this[key];
    },

    write: function (key) {
        document.write(this[key]);
    }
}


var Downloader = {
    downloads: [],

    init: function (sources) {
        for (i in sources) {
            var source = new Download(sources[i]);
            this.downloads.push(source);
        }
    },

    select: function () {
        var ua = navigator.userAgent;
        for (i in this.downloads) {
            if (this.downloads[i].matches(ua)) {
                return this.downloads[i];
            }
        }
        return null;
    },

    listall: function () {
        // copy the download list
        var downloads = this.downloads.slice(0);
        // alpha-sort it by description (case-folded)
        downloads.sort(function (a, b) {
            a = a.desc.toLowerCase();
            b = b.desc.toLowerCase();
            return (b < a) - (a < b);
        });

        for (i in downloads) {
            var dl = downloads[i];
            document.write('<tr>\n<td>' + dl.desc + '</td>' +
                           '<td></td>' +
                           '<td><a href="' + dl.url + '">download</a></td>' +
                           '</tr>');
        }
    }
};
