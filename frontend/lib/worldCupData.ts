export interface CountryStats {
  name: string;
  wins: number;
  draws: number;
  losses: number;
  matches: number;
  peakStage: string;
  confed: string;
}

export const worldCupStats: Record<string, CountryStats> = {
  // === CONMEBOL ===
  "Brazil": { name: "Brazil", wins: 76, draws: 19, losses: 19, matches: 114, peakStage: "Champions (5x)", confed: "CONMEBOL" },
  "Argentina": { name: "Argentina", wins: 49, draws: 16, losses: 23, matches: 88, peakStage: "Champions (3x)", confed: "CONMEBOL" },
  "Uruguay": { name: "Uruguay", wins: 25, draws: 13, losses: 20, matches: 58, peakStage: "Champions (2x)", confed: "CONMEBOL" },
  "Chile": { name: "Chile", wins: 11, draws: 7, losses: 15, matches: 33, peakStage: "Third Place (1962)", confed: "CONMEBOL" },
  "Colombia": { name: "Colombia", wins: 9, draws: 3, losses: 10, matches: 22, peakStage: "Quarter-finals (2014)", confed: "CONMEBOL" },
  "Paraguay": { name: "Paraguay", wins: 7, draws: 10, losses: 10, matches: 27, peakStage: "Quarter-finals (2010)", confed: "CONMEBOL" },
  "Peru": { name: "Peru", wins: 5, draws: 3, losses: 10, matches: 18, peakStage: "Quarter-finals", confed: "CONMEBOL" },
  "Ecuador": { name: "Ecuador", wins: 5, draws: 2, losses: 6, matches: 13, peakStage: "Round of 16 (2006)", confed: "CONMEBOL" },
  "Bolivia": { name: "Bolivia", wins: 0, draws: 1, losses: 5, matches: 6, peakStage: "Group Stage", confed: "CONMEBOL" },

  // === UEFA ===
  "Germany": { name: "Germany", wins: 68, draws: 21, losses: 23, matches: 112, peakStage: "Champions (4x)", confed: "UEFA" },
  "Italy": { name: "Italy", wins: 45, draws: 21, losses: 17, matches: 83, peakStage: "Champions (4x)", confed: "UEFA" },
  "France": { name: "France", wins: 39, draws: 14, losses: 20, matches: 73, peakStage: "Champions (2x)", confed: "UEFA" },
  "England": { name: "England", wins: 32, draws: 22, losses: 20, matches: 74, peakStage: "Champions (1966)", confed: "UEFA" },
  "Netherlands": { name: "Netherlands", wins: 32, draws: 14, losses: 9, matches: 55, peakStage: "Runners-up (3x)", confed: "UEFA" },
  "Spain": { name: "Spain", wins: 31, draws: 17, losses: 19, matches: 67, peakStage: "Champions (2010)", confed: "UEFA" },
  "Belgium": { name: "Belgium", wins: 21, draws: 10, losses: 20, matches: 51, peakStage: "Third Place (2018)", confed: "UEFA" },
  "Sweden": { name: "Sweden", wins: 20, draws: 13, losses: 18, matches: 51, peakStage: "Runners-up (1958)", confed: "UEFA" },
  "Poland": { name: "Poland", wins: 17, draws: 6, losses: 15, matches: 38, peakStage: "Third Place (2x)", confed: "UEFA" },
  "Portugal": { name: "Portugal", wins: 17, draws: 6, losses: 12, matches: 35, peakStage: "Third Place (1966)", confed: "UEFA" },
  "Hungary": { name: "Hungary", wins: 15, draws: 3, losses: 14, matches: 32, peakStage: "Runners-up (2x)", confed: "UEFA" },
  "Switzerland": { name: "Switzerland", wins: 14, draws: 9, losses: 19, matches: 42, peakStage: "Quarter-finals (3x)", confed: "UEFA" },
  "Croatia": { name: "Croatia", wins: 13, draws: 8, losses: 10, matches: 31, peakStage: "Runners-up (2018)", confed: "UEFA" },
  "Austria": { name: "Austria", wins: 12, draws: 4, losses: 14, matches: 30, peakStage: "Third Place (1954)", confed: "UEFA" },
  "Denmark": { name: "Denmark", wins: 9, draws: 5, losses: 10, matches: 24, peakStage: "Quarter-finals (1998)", confed: "UEFA" },
  "Romania": { name: "Romania", wins: 6, draws: 5, losses: 10, matches: 21, peakStage: "Quarter-finals (1994)", confed: "UEFA" },
  "Russia": { name: "Russia", wins: 5, draws: 2, losses: 7, matches: 14, peakStage: "Quarter-finals (2018)", confed: "UEFA" },
  "Scotland": { name: "Scotland", wins: 5, draws: 7, losses: 12, matches: 24, peakStage: "Group Stage", confed: "UEFA" },
  "Turkey": { name: "Turkey", wins: 5, draws: 1, losses: 4, matches: 10, peakStage: "Third Place (2002)", confed: "UEFA" },
  "Bulgaria": { name: "Bulgaria", wins: 3, draws: 8, losses: 15, matches: 26, peakStage: "Fourth Place (1994)", confed: "UEFA" },
  "Northern Ireland": { name: "Northern Ireland", wins: 3, draws: 5, losses: 5, matches: 13, peakStage: "Quarter-finals (1958)", confed: "UEFA" },
  "Ireland": { name: "Ireland", wins: 2, draws: 8, losses: 3, matches: 13, peakStage: "Quarter-finals (1990)", confed: "UEFA" },
  "Norway": { name: "Norway", wins: 2, draws: 3, losses: 3, matches: 8, peakStage: "Round of 16 (1998)", confed: "UEFA" },
  "Ukraine": { name: "Ukraine", wins: 2, draws: 1, losses: 2, matches: 5, peakStage: "Quarter-finals (2006)", confed: "UEFA" },
  "Greece": { name: "Greece", wins: 2, draws: 2, losses: 6, matches: 10, peakStage: "Round of 16 (2014)", confed: "UEFA" },
  "Serbia": { name: "Serbia", wins: 2, draws: 1, losses: 6, matches: 9, peakStage: "Group Stage", confed: "UEFA" },
  "Wales": { name: "Wales", wins: 1, draws: 4, losses: 3, matches: 8, peakStage: "Quarter-finals (1958)", confed: "UEFA" },
  "Slovakia": { name: "Slovakia", wins: 1, draws: 1, losses: 2, matches: 4, peakStage: "Round of 16 (2010)", confed: "UEFA" },
  "Slovenia": { name: "Slovenia", wins: 1, draws: 1, losses: 4, matches: 6, peakStage: "Group Stage", confed: "UEFA" },
  "Bosnia and Herzegovina": { name: "Bosnia and Herzegovina", wins: 1, draws: 0, losses: 2, matches: 3, peakStage: "Group Stage (2014)", confed: "UEFA" },
  "Iceland": { name: "Iceland", wins: 0, draws: 1, losses: 2, matches: 3, peakStage: "Group Stage (2018)", confed: "UEFA" },

  // === CAF ===
  "Nigeria": { name: "Nigeria", wins: 6, draws: 3, losses: 12, matches: 21, peakStage: "Round of 16", confed: "CAF" },
  "Morocco": { name: "Morocco", wins: 5, draws: 7, losses: 11, matches: 23, peakStage: "Fourth Place (2022)", confed: "CAF" },
  "Cameroon": { name: "Cameroon", wins: 5, draws: 8, losses: 13, matches: 26, peakStage: "Quarter-finals (1990)", confed: "CAF" },
  "Senegal": { name: "Senegal", wins: 5, draws: 3, losses: 5, matches: 13, peakStage: "Quarter-finals (2002)", confed: "CAF" },
  "Ghana": { name: "Ghana", wins: 4, draws: 3, losses: 8, matches: 15, peakStage: "Quarter-finals (2010)", confed: "CAF" },
  "Tunisia": { name: "Tunisia", wins: 3, draws: 5, losses: 10, matches: 18, peakStage: "Group Stage", confed: "CAF" },
  "Algeria": { name: "Algeria", wins: 3, draws: 3, losses: 8, matches: 14, peakStage: "Round of 16 (2014)", confed: "CAF" },
  "Ivory Coast": { name: "Ivory Coast", wins: 3, draws: 1, losses: 5, matches: 9, peakStage: "Group Stage", confed: "CAF" },
  "South Africa": { name: "South Africa", wins: 2, draws: 4, losses: 4, matches: 10, peakStage: "Group Stage", confed: "CAF" },
  "Egypt": { name: "Egypt", wins: 0, draws: 2, losses: 5, matches: 7, peakStage: "Group Stage", confed: "CAF" },
  "Angola": { name: "Angola", wins: 0, draws: 2, losses: 1, matches: 3, peakStage: "Group Stage (2006)", confed: "CAF" },
  "Togo": { name: "Togo", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (2006)", confed: "CAF" },

  // === AFC ===
  "South Korea": { name: "South Korea", wins: 7, draws: 11, losses: 21, matches: 39, peakStage: "Fourth Place (2002)", confed: "AFC" },
  "Japan": { name: "Japan", wins: 7, draws: 6, losses: 13, matches: 26, peakStage: "Round of 16", confed: "AFC" },
  "Australia": { name: "Australia", wins: 4, draws: 5, losses: 12, matches: 21, peakStage: "Round of 16", confed: "AFC" },
  "Saudi Arabia": { name: "Saudi Arabia", wins: 4, draws: 2, losses: 13, matches: 19, peakStage: "Round of 16 (1994)", confed: "AFC" },
  "Iran": { name: "Iran", wins: 3, draws: 4, losses: 11, matches: 18, peakStage: "Group Stage", confed: "AFC" },
  "North Korea": { name: "North Korea", wins: 1, draws: 1, losses: 5, matches: 7, peakStage: "Quarter-finals (1966)", confed: "AFC" },
  "Iraq": { name: "Iraq", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (1986)", confed: "AFC" },
  "United Arab Emirates": { name: "United Arab Emirates", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (1990)", confed: "AFC" },
  "China": { name: "China", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (2002)", confed: "AFC" },
  "Kuwait": { name: "Kuwait", wins: 0, draws: 1, losses: 2, matches: 3, peakStage: "Group Stage (1982)", confed: "AFC" },
  "Qatar": { name: "Qatar", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (2022)", confed: "AFC" },

  // === CONCACAF ===
  "Mexico": { name: "Mexico", wins: 17, draws: 15, losses: 29, matches: 61, peakStage: "Quarter-finals (2x)", confed: "CONCACAF" },
  "United States of America": { name: "United States of America", wins: 10, draws: 8, losses: 20, matches: 38, peakStage: "Third Place (1930)", confed: "CONCACAF" },
  "Costa Rica": { name: "Costa Rica", wins: 5, draws: 5, losses: 8, matches: 18, peakStage: "Quarter-finals (2014)", confed: "CONCACAF" },
  "Honduras": { name: "Honduras", wins: 0, draws: 3, losses: 6, matches: 9, peakStage: "Group Stage", confed: "CONCACAF" },
  "Canada": { name: "Canada", wins: 0, draws: 0, losses: 6, matches: 6, peakStage: "Group Stage", confed: "CONCACAF" },
  "El Salvador": { name: "El Salvador", wins: 0, draws: 0, losses: 6, matches: 6, peakStage: "Group Stage", confed: "CONCACAF" },
  "Jamaica": { name: "Jamaica", wins: 1, draws: 0, losses: 2, matches: 3, peakStage: "Group Stage (1998)", confed: "CONCACAF" },
  "Haiti": { name: "Haiti", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (1974)", confed: "CONCACAF" },
  "Trinidad and Tobago": { name: "Trinidad and Tobago", wins: 0, draws: 1, losses: 2, matches: 3, peakStage: "Group Stage (2006)", confed: "CONCACAF" },
  "Panama": { name: "Panama", wins: 0, draws: 0, losses: 3, matches: 3, peakStage: "Group Stage (2018)", confed: "CONCACAF" },

  // === OFC ===
  "New Zealand": { name: "New Zealand", wins: 0, draws: 3, losses: 3, matches: 6, peakStage: "Group Stage", confed: "OFC" }
};
