import { error } from '@sveltejs/kit';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

export async function load() {
	const dinnersPath = path.resolve(process.cwd(), '..', 'dinners.json');

	try {
		const raw = await readFile(dinnersPath, 'utf8');
		const dinners = JSON.parse(raw);
		return { dinners };
	} catch (err) {
		throw error(500, 'Failed to load dinners.json');
	}
}

