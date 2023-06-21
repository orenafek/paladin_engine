class Customization {
    static matches(data) {
        return true;
    }

    static getFormattedData(data) {
        return {
          	"contentType": "text/plain",
          	"content": data
        };
    }
}