import axios from "axios";

export class PreviewService {
  async fetchPreview(url: string) {
    const response = await axios.get(url, {
      timeout: 3000,
      validateStatus: () => true
    });

    return {
      success: true,
      status_code: response.status,
      content_type: response.headers["content-type"],
      data_preview: typeof response.data === "string" ? response.data : JSON.stringify(response.data)
    };
  }
}
