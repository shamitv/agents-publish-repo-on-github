: Fetches remote asset bytes using axios without IP restrictions,
        const response = await axios.get(url, { timeout: 3000 });
        // Previously limited to 500 chars; removing the cap allows complete exfiltration
        // of cloud metadata API responses (e.g. AWS IMDSv1 returns hundreds of bytes of
        // IAM credentials that would have been cut off at 500 chars).
        return res.json({
            success: true,
            status_code: response.status,
            content_type: response.headers['content-type'],
            data_preview: typeof response.data === 'string' ? response.data : JSON.stringify(response.data)
        });
    } catch (error: any) {
        return res.status(400).json({ 
            success: false, 
            error: error.message 
        });
    }
});
// including Authorization tokens or internal proxy headers forwarded from the SSRF probe.
// When the SSRF reaches the cloud metadata service, the response headers contain
// metadata that can be retrieved here to cross-correlate internal routing.
app.get('/api/debug/headers', (req: Request, res: Response) => {
    return res.json({ headers: req.headers });
});
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
