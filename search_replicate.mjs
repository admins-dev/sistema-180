import axios from 'axios';

async function searchReplicate() {
    try {
        console.log("Searching for working face-ID models...");
        // Use the unofficial search endpoint to find active models
        const queries = ['pulid', 'instantid', 'faceid'];

        for (const q of queries) {
            console.log(`\nResults for '${q}':`);
            const response = await axios.get(`https://replicate.com/api/models?query=${q}`);
            const models = response.data.results || [];

            models.slice(0, 5).forEach(m => {
                console.log(`- ${m.owner}/${m.name}: ${m.description?.substring(0, 50)}...`);
            });
        }
    } catch (e) {
        console.error("Search failed:", e.message);
    }
}

searchReplicate();
