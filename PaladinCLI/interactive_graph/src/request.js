async function request(req) {
    const gResponse = await fetch(window.location.origin + "/" + req, {
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