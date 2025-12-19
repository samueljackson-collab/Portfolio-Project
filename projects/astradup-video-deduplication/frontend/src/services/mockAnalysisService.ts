import type { VideoMetadata, EnrichedMetadata } from '../types';

const MOCK_TITLES = [
  "Inception", "The Dark Knight", "Interstellar", "Pulp Fiction", "Forrest Gump",
  "The Matrix", "Goodfellas", "The Shawshank Redemption", "Fight Club", "The Godfather"
];
const MOCK_ACTORS = [
  "Leonardo DiCaprio", "Tom Hardy", "Christian Bale", "Heath Ledger", "Matthew McConaughey",
  "Anne Hathaway", "John Travolta", "Samuel L. Jackson", "Tom Hanks", "Robin Wright",
  "Keanu Reeves", "Laurence Fishburne", "Robert De Niro", "Ray Liotta", "Tim Robbins",
  "Morgan Freeman", "Brad Pitt", "Edward Norton", "Marlon Brando", "Al Pacino"
];

const randomChoice = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
const randomInt = (min: number, max: number): number => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min: number, max: number, decimals: number = 1): number => {
  const str = (Math.random() * (max - min) + min).toFixed(decimals);
  return parseFloat(str);
};

// Simulates extracting basic metadata and generating a thumbnail
export const mockVideoAnalysis = (file: File): Promise<{ metadata: VideoMetadata }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const videoId = `vid_${Math.random().toString(36).substr(2, 9)}`;
      const metadata: VideoMetadata = {
        id: videoId,
        fileName: file.name,
        fileSize: file.size,
        duration: randomInt(60, 180) * 60, // 1-3 hours in seconds
        width: 1920,
        height: 1080,
        frameRate: 24,
        thumbnail: `https://picsum.photos/seed/${videoId}/400/225`,
      };
      resolve({ metadata });
    }, randomInt(1500, 3000));
  });
};

// Simulates fetching enriched data from IMDB/Gemini
export const mockMetadataFetch = (fileName: string): Promise<EnrichedMetadata> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const title = randomChoice(MOCK_TITLES);
        const enriched: EnrichedMetadata = {
          title: title,
          year: randomInt(1990, 2023),
          genres: [randomChoice(['Action', 'Sci-Fi', 'Drama']), randomChoice(['Thriller', 'Crime', 'Adventure'])],
          actors: [randomChoice(MOCK_ACTORS), randomChoice(MOCK_ACTORS), randomChoice(MOCK_ACTORS)],
          director: randomChoice(['Christopher Nolan', 'Quentin Tarantino', 'Frank Darabont']),
          plot: `A mock plot for the movie titled '${title}'. This is a compelling story about...`,
          imdbRating: randomFloat(7.5, 9.5),
          source: randomChoice(['IMDB', 'TMDb']),
        };
        resolve(enriched);
      }, randomInt(1000, 2000));
    });
  };
