window.onload = (_event) => {
    let anchorPoint = document.getElementsByClassName("article-header-buttons")[0]?.parentElement;
    if (anchorPoint == null) {
        console.error("could not find the version tag anchor point");
        return;
    }
    displayVersionFor(anchorPoint, "/latest.dat", "Mercurial");

    anchorPoint = document.getElementById("windows-badge-marker")?.parentElement?.parentElement;
    if (anchorPoint == null) {
        console.error("could not find the Windows version tag anchor point");
        return;
    }
    displayVersionFor(anchorPoint, "/release/windows/latest.dat", "Mercurial for Windows", true);

    anchorPoint = document.getElementById("tortoisehg-badge-marker")?.parentElement?.parentElement;
    if (anchorPoint == null) {
        console.error("could not find the TortoiseHg version tag anchor point");
        return;
    }
    displayVersionFor(anchorPoint, "/release/tortoisehg/latest.dat", "TortoiseHg", true);
};

function displayVersionFor(anchorPoint, url, name, verbose) {
    window.fetch(url).then((res) => {
        if (!res.ok) {
            return Promise.reject(`failed to fetch latest ${name} version`);
        }
        console.info(`successfully fetched version info for ${name}`);
        return res.text();
    }).then((contents) => {
        const latest = extractLatest(contents);
        if (latest != null) {
            const versionSpan = document.createElement("span");
            versionSpan.setAttribute("title", `Latest ${name} version`);
            versionSpan.classList.add("hg-version-tag");
            if (verbose) {
                versionSpan.innerHTML = `Latest ${name}: ${latest}`;
            } else {
                versionSpan.innerHTML = `Latest: ${latest}`;
            }
            anchorPoint.prepend(versionSpan);
        } else {
            return Promise.reject(`invalid latest.dat for ${name}: ${contents}`);
        }
    });
}

function extractLatest(contents) {
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
