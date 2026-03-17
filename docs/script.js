let allStatsData = null;
let currentYear = '2026'; // Default to 2026

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to load from embedded script tag first (for offline/file:// access)
    const embeddedData = document.getElementById('statsData');
    if (embeddedData && embeddedData.textContent) {
        try {
            allStatsData = JSON.parse(embeddedData.textContent);
            console.log('✓ Stats loaded from embedded data');
            initializeYearSelector();
            displayStats(currentYear);
            return;
        } catch (e) {
            console.log('Failed to parse embedded data:', e);
        }
    }
    
    // Fallback to fetch (for server/GitHub Pages)
    loadStats();
});

async function loadStats() {
    try {
        const response = await fetch('stats.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allStatsData = await response.json();
        console.log('✓ Stats loaded from fetch');
        initializeYearSelector();
        displayStats(currentYear);
    } catch (error) {
        console.error('Error loading stats:', error);
        // Show error message to user
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #666;">
                    <h2>⚠️ Unable to Load Statistics</h2>
                    <p style="margin: 20px 0;">Could not load cricket statistics.</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    <div style="text-align: left; max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <p><strong>If viewing locally:</strong></p>
                        <ol>
                            <li>Make sure you're in the docs folder</li>
                            <li>Start a local server: <code style="background: white; padding: 2px 8px; border-radius: 4px;">python3 -m http.server 8000</code></li>
                            <li>Visit: <a href="http://localhost:8000">http://localhost:8000</a></li>
                        </ol>
                        <p style="margin-top: 15px;"><strong>Or:</strong> Open the browser console (F12) to see detailed errors.</p>
                    </div>
                </div>
            `;
        }
    }
}

function initializeYearSelector() {
    const yearSelect = document.getElementById('yearSelect');
    if (yearSelect && allStatsData) {
        // Set default to current year
        yearSelect.value = currentYear;
        
        // Disable years with no data
        const options = yearSelect.querySelectorAll('option');
        options.forEach(option => {
            const year = option.value;
            if (!allStatsData[year] || !allStatsData[year].summary || !allStatsData[year].summary.total_matches) {
                option.disabled = true;
                option.textContent += ' (No data)';
            }
        });
    }
}

function changeYear(year) {
    currentYear = year;
    displayStats(year);
    console.log(`Switched to ${year} season`);
}

function displayStats(year) {
    const statsData = allStatsData[year];
    
    if (!statsData || !statsData.summary) {
        console.warn(`No data available for ${year}`);
        showNoDataMessage(year);
        return;
    }
    
    // Update summary
    document.getElementById('lastUpdated').textContent = new Date(statsData.last_updated).toLocaleDateString();
    document.getElementById('totalMatches').textContent = statsData.summary.total_matches || '-';
    document.getElementById('totalRuns').textContent = statsData.summary.total_runs || '-';
    document.getElementById('totalPlayers').textContent = statsData.summary.total_players || '-';
    
    if (statsData.summary.date_range) {
        const start = new Date(statsData.summary.date_range.start).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
        const end = new Date(statsData.summary.date_range.end).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        document.getElementById('dateRange').textContent = `${start} - ${end}`;
    } else {
        document.getElementById('dateRange').textContent = '-';
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
        displayLeaderboard('mostFours', statsData.batting.leaderboards.most_fours, 
            ['batsman', 'fours', 'runs', 'innings']);
        displayLeaderboard('mostSixes', statsData.batting.leaderboards.most_sixes, 
            ['batsman', 'sixes', 'runs', 'innings']);
        
        // Display all players
        displayAllPlayers(statsData.batting.season_stats);
    } else {
        clearLeaderboards();
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

function showNoDataMessage(year) {
    const tables = document.querySelectorAll('table tbody');
    tables.forEach(tbody => {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 20px; color: #888;">
                    No data available for ${year} season yet
                </td>
            </tr>
        `;
    });
    
    document.getElementById('dateRange').textContent = 'No matches yet';
}

function clearLeaderboards() {
    const tables = ['topRunScorers', 'highestScores', 'bestAverages', 'bestStrikeRates', 
                    'mostFours', 'mostSixes', 'topWicketTakers', 'bestFigures', 'bestEconomy'];
    tables.forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (tbody) tbody.innerHTML = '';
    });
}

function displayLeaderboard(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No data</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    data.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            ${columns.map(col => `<td>${formatValue(row[col], col)}</td>`).join('')}
        `;
        tbody.appendChild(tr);
    });
}

function displayAllPlayers(players) {
    const tbody = document.getElementById('allPlayersList');
    if (!tbody) return;
    
    if (!players || players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No players</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    players.forEach(player => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${player.batsman}</td>
            <td>${formatValue(player.innings, 'innings')}</td>
            <td>${formatValue(player.runs, 'runs')}</td>
            <td>${formatValue(player.average, 'average')}</td>
            <td>${formatValue(player.sr, 'sr')}</td>
            <td>${formatValue(player.balls, 'balls')}</td>
            <td>${formatValue(player.fours, 'fours')}</td>
            <td>${formatValue(player.sixes, 'sixes')}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatValue(val, columnName) {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') {
        if (isNaN(val)) return '-';
        
        // Integer fields - no decimal places
        const integerFields = ['runs', 'innings', 'balls', 'fours', 'sixes', 'wickets', 'overs', 'maidens'];
        if (columnName && integerFields.includes(columnName)) {
            return Math.round(val).toString();
        }
        
        // Decimal fields (average, sr, economy)
        return val.toFixed(2);
    }
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
