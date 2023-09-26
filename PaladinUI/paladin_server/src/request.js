export async function request(req) {
    const req_with_lr = req.replace(/\r\n|\r|\n/g, '<br>');
    const gResponse = await fetch(window.location.origin + "/" + req_with_lr, {
        headers: {
            "Accept": "application-json"
        }
    });
    return gResponse?.json();
}

export async function request_debug_info(req, ...args) {
    return new Object(
        (await request("debug_info/" + req +
                (args.length > 0 ? ("/" + args.join("/")) : ""))
        )["result"][req]);
}

export async function upload(content, server_path) {
    await fetch(server_path, {
        method: 'POST',
        headers: {
            'Accept': 'application-json'
        },
        body: content
    });
}

export async function reset_aux_file() {
    await fetch("reset_aux_file", {
        method: 'GET',
        headers: {
            "Accept": "application-json"
        },
    });
}
