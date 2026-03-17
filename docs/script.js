let statsData = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
});

async function loadStats() {
    try {
        const response = await fetch('stats.json');
        statsData = await response.json();
        displayStats();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function displayStats() {
    // Update summary
    document.getElementById('lastUpdated').textContent = new Date(statsData.last_updated).toLocaleDateString();
    document.getElementById('totalMatches').textContent = statsData.summary.total_matches || '-';
    document.getElementById('totalRuns').textContent = statsData.summary.total_runs || '-';
    document.getElementById('totalPlayers').textContent = statsData.summary.total_players || '-';
    
    if (statsData.summary.date_range) {
        const start = new Date(statsData.summary.date_range.start).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
        const end = new Date(statsData.summary.date_range.end).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        document.getElementById('dateRange').textContent = `${start} - ${end}`;
    }
    
    // Display batting leaderboards
    if (statsData.batting && statsData.batting.leaderboards) {
        displayLeaderboard('topRunScorers', statsData.batting.leaderboards.top_run_scorers, 
            ['batsman', 'runs', 'innings', 'average', 'sr']);
        displayLeaderboard('highestScores', statsData.batting.leaderboards.highest_scores, 
            ['batsman', 'runs', 'balls', 'sr']);
        displayLeaderboard('bestAverages', statsData.batting.leaderboards.best_averages, 
            ['batsman', 'average', 'runs', 'innings']);
        displayLeaderboard('bestStrikeRates', statsData.batting.leaderboards.best_strike_rates, 
            ['batsman', 'sr', 'runs', 'balls']);
        
        // Display all players
        displayAllPlayers(statsData.batting.season_stats);
    }
    
    // Display bowling leaderboards
    if (statsData.bowling && statsData.bowling.leaderboards) {
        displayLeaderboard('topWicketTakers', statsData.bowling.leaderboards.top_wicket_takers, 
            ['bowler', 'wickets', 'average', 'economy']);
        displayLeaderboard('bestFigures', statsData.bowling.leaderboards.best_figures, 
            ['bowler', 'wickets', 'runs', 'overs']);
        displayLeaderboard('bestEconomy', statsData.bowling.leaderboards.best_economy, 
            ['bowler', 'economy', 'overs', 'wickets']);
    }
}

function displayLeaderboard(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody || !data) return;
    
    tbody.innerHTML = '';
    data.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            ${columns.map(col => `<td>${formatValue(row[col])}</td>`).join('')}
        `;
        tbody.appendChild(tr);
    });
}

function displayAllPlayers(players) {
    const tbody = document.getElementById('allPlayersList');
    if (!tbody || !players) return;
    
    tbody.innerHTML = '';
    players.forEach(player => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${player.batsman}</td>
            <td>${player.innings}</td>
            <td>${player.runs}</td>
            <td>${formatValue(player.average)}</td>
            <td>${formatValue(player.sr)}</td>
            <td>${player.balls}</td>
            <td>${player.fours}</td>
            <td>${player.sixes}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatValue(val) {
    if (val === null || val === undefined || val === 'NaN' || isNaN(val)) return '-';
    if (typeof val === 'number') return val.toFixed(2);
    return val;
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function filterPlayers() {
    const searchTerm = document.getElementById('playerSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#allPlayersList tr');
    
    rows.forEach(row => {
        const playerName = row.cells[0].textContent.toLowerCase();
        row.style.display = playerName.includes(searchTerm) ? '' : 'none';
    });
}

function sortTable(columnIndex) {
    // Simple table sorting (can be enhanced)
    const table = document.getElementById('allPlayersTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent;
        const bVal = b.cells[columnIndex].textContent;
        
        // Try numeric comparison first
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum;
        }
        
        // String comparison
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
