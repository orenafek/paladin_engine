export async function request(func, args) {
    const gResponse = await fetch('http://localhost:8888/' + func,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'args': args})
        });
    return gResponse?.json();
}