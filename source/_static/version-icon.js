// Fetches the latest version of Mercurial and displays it in the header
window.onload = (_event) => {
    const headerButton = document.getElementsByClassName("article-header-buttons")[0];
    if (headerButton == null) {
        console.error("could not find the version tag anchor point");
        return;
    }
    const anchorPoint = headerButton.parentElement;
    if (anchorPoint == null) {
        console.error("could not find the version tag anchor point");
        return;
    }
    window.fetch("/latest.dat").then((res) => {
        if (!res.ok) {
            return Promise.reject("failed to fetch latest Mercurial version");
        }
        console.info("successfully fetched version info")
        return res.text();
    }).then((contents) => {
        const latest = extractLatestHg(contents);
        if (latest != null) {
            const versionSpan = document.createElement("span");
            versionSpan.setAttribute("title", "Latest Mercurial version");
            versionSpan.setAttribute("id", "hg-version-tag");
            versionSpan.innerHTML = latest;
            anchorPoint.prepend(versionSpan);
        } else {
            return Promise.reject(`invalid latest.dat: ${latest}`);
        }
    });
};

function extractLatestHg(contents) {
    const versionPattern = /(\d+)\t([^\t]*)\t.*/;
    const lines = contents.split("\n");
    const versions = lines.reduce((acc, curr) => {
        const matches = versionPattern.exec(curr);
        if (matches == null) {
            return acc;
        }
        const priority = matches[1];
        const version = matches[2];
        if (priority == null || version == null) {
            return acc;
        }
        const priorityInt = parseInt(priority, 10);
        if (!isNaN(priorityInt)) {
            acc.push([priorityInt, version]);
        }
        return acc;
    }, []);
    const highestPriorityVersion = versions.sort((a, b) => b[0] - a[0])[0];
    if (highestPriorityVersion != null) {
        return highestPriorityVersion[1];
    }
}
