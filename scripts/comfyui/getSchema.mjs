import axios from 'axios';

async function get() {
    const res = await axios.get('https://api.replicate.com/v1/models/lucataco/faceswap/versions/9a4298548422074c3f57258c5d544497314ae41183cf0c150b0cd924a4ea1101', {
        headers: { Authorization: 'Token ' + process.env.REPLICATE_API_TOKEN }
    });
    console.log(JSON.stringify(res.data.openapi_schema.components.schemas.Input, null, 2));
}
get().catch(e => console.error(e.response?.data || e.message));
