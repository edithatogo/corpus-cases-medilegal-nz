import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://edithatogo.github.io',
  base: '/corpus-cases-medilegal-nz/',
  integrations: [
    mdx(),
    sitemap(),
    starlight({
      title: 'Corpus Cases Medilegal NZ',
      description: 'Legal NZ documentation portal for Corpus Cases Medilegal NZ.',
      sidebar: [
        { label: 'Start', items: ['index', 'docs-tooling-audit'] },
      ],
    }),
  ],
});
