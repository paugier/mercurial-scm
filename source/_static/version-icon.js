window.onload = (_event) => {
    // Fetch the latest version of Mercurial
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
    window.fetch("/_static/latest.dat").then((res) => {
        if (!res.ok) {
            return Promise.reject("failed to fetch latest Mercurial version");
        }
        console.info("successfully fetched version info")
        return res.text();
    }).then((contents) => {
        const versionPattern = /\d+\t([^\t]*)\t.*/;
        const match = versionPattern.exec(contents)[1];
        if (match != null) {
            const versionSpan = document.createElement("span");
            versionSpan.setAttribute("title", "Latest Mercurial version");
            versionSpan.setAttribute("id", "hg-version-tag");
            versionSpan.innerHTML = match;
            anchorPoint.prepend(versionSpan);
        } else {
            return Promise.reject(`invalid latest.dat: ${match}`);
        }
    });
};
