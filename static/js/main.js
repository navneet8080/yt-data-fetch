document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();

    // Event Listeners
    document.getElementById('refresh-btn').addEventListener('click', (e) => {
        e.preventDefault();
        refreshData();
    });
    
    document.getElementById('export-sheets-btn').addEventListener('click', (e) => {
        e.preventDefault();
        exportToSheets();
    });
});

async function fetchDashboardData() {
    try {
        const response = await fetch('/videos');
        const videos = await response.json();
        
        if (!videos || videos.length === 0) {
            document.getElementById('videos-table-body').innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No videos found. Click 'Sync Data' to fetch from YouTube.</td></tr>`;
            return;
        }

        // Calculate Totals
        let totalViews = 0;
        let totalLikes = 0;
        let totalComments = 0;

        videos.forEach(v => {
            totalViews += parseInt(v.view_count || 0);
            totalLikes += parseInt(v.like_count || 0);
            totalComments += parseInt(v.comment_count || 0);
        });

        // Update Stat Cards with animation
        animateValue('total-videos', 0, videos.length, 1000);
        animateValue('total-views', 0, totalViews, 1000);
        animateValue('total-likes', 0, totalLikes, 1000);
        animateValue('total-comments', 0, totalComments, 1000);

        // Populate Table
        renderTable(videos);
    } catch (error) {
        console.error("Error fetching data:", error);
        showToast("Error loading dashboard data", true);
    }
}

function renderTable(videos) {
    const tbody = document.getElementById('videos-table-body');
    tbody.innerHTML = '';
    
    // Sort by published date descending (newest first)
    const sortedVideos = [...videos].sort((a, b) => new Date(b.published_at) - new Date(a.published_at));

    // Display top 30 videos
    sortedVideos.slice(0, 30).forEach(video => {
        const tr = document.createElement('tr');
        
        const date = new Date(video.published_at).toLocaleDateString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric'
        });

        tr.innerHTML = `
            <td>
                <img src="https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg" alt="Thumbnail" class="video-thumb" loading="lazy">
            </td>
            <td><div class="video-title" title="${video.title}">${video.title}</div></td>
            <td>${date}</td>
            <td><span class="stat-badge"><i class="fas fa-eye" style="color:var(--text-muted); font-size:10px;"></i> ${formatNumber(video.view_count)}</span></td>
            <td><span class="stat-badge"><i class="fas fa-thumbs-up" style="color:var(--text-muted); font-size:10px;"></i> ${formatNumber(video.like_count)}</span></td>
            <td><span class="stat-badge"><i class="fas fa-comment" style="color:var(--text-muted); font-size:10px;"></i> ${formatNumber(video.comment_count)}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

async function refreshData() {
    showToast("Syncing data from YouTube... This may take a moment.");
    try {
        const res = await fetch('/refresh');
        const data = await res.json();
        if (data.status === 'success') {
            showToast(`Success! Fetched ${data.fetched} videos.`);
            fetchDashboardData();
        } else {
            showToast(`Error: ${data.message}`, true);
        }
    } catch (error) {
        showToast("Error syncing data", true);
    }
}

async function exportToSheets() {
    showToast("Exporting to Google Sheets...");
    try {
        const res = await fetch('/export_sheets');
        const data = await res.json();
        if (data.status === 'success') {
            showToast("Export successful!");
        } else {
            showToast(`Error: ${data.message}`, true);
        }
    } catch (error) {
        showToast("Error exporting to sheets", true);
    }
}

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-message');
    
    // Add icon based on status
    const icon = isError ? '<i class="fas fa-exclamation-circle"></i>' : '<i class="fas fa-check-circle"></i>';
    msgEl.innerHTML = `${icon} ${message}`;
    
    if (isError) {
        toast.style.backgroundColor = '#ef4444'; // Red
    } else {
        toast.style.backgroundColor = '#6366f1'; // Indigo
    }
    
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return Number(num).toLocaleString();
}

function animateValue(id, start, end, duration) {
    if (start === end) {
        document.getElementById(id).textContent = formatNumber(end);
        return;
    }
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // easeOutQuart
        const easeProgress = 1 - Math.pow(1 - progress, 4);
        obj.innerHTML = formatNumber(Math.floor(easeProgress * (end - start) + start));
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}
