import { promises as fs } from 'fs'
import path from 'path'
import url from 'url'
import sharp from 'sharp'

const __dirname = path.dirname(url.fileURLToPath(import.meta.url))
const frontendDir = path.resolve(__dirname, '..')
const repoRoot = path.resolve(frontendDir, '..')
const inputDir = path.join(repoRoot, 'static', 'img', 'logos')
const outputDir = path.join(inputDir, 'png')
const sizes = [32, 64, 128, 256]
const files = [
  'logo_ai_report_v2.svg',
  'logo_report_analysis_v2.svg',
  'logo_geo_isometric_v2.svg',
  'logo_policy_research_v2.svg'
]

await fs.mkdir(outputDir, { recursive: true })

for (const file of files) {
  const base = path.parse(file).name
  const svgPath = path.join(inputDir, file)
  const svgBuffer = await fs.readFile(svgPath)
  for (const size of sizes) {
    const outPath = path.join(outputDir, `${base}-${size}.png`)
    await sharp(svgBuffer)
      .resize(size, size, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(outPath)
  }
}

console.log('Done: PNG exported to', outputDir)
