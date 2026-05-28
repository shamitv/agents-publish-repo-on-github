import axios from "axios";

export class PreviewService {
  async fetchPreview(url: string) {
    // CHAIN LINK 2 (chain-01): User-controlled URL is fetched server-side with no internal network restrictions.
    // VULNERABILITY A10: axios fetches arbitrary URLs, enabling HTTP SSRF.
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
