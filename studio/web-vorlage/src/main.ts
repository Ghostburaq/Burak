import "./style.css";
import gsap from "gsap";
import * as THREE from "three";

// Text-Animation beim Laden
gsap.from(".hero", { y: 40, opacity: 0, duration: 0.9, stagger: 0.12, ease: "power3.out" });

// 3D-Hintergrund: rotierender Körper mit Drahtgitter
const canvas = document.querySelector<HTMLCanvasElement>("#szene")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
camera.position.z = 6;

const koerper = new THREE.Mesh(
  new THREE.IcosahedronGeometry(2, 1),
  new THREE.MeshStandardMaterial({ color: 0xf5c400, flatShading: true, roughness: 0.4 }),
);
koerper.add(new THREE.LineSegments(
  new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(2.02, 1)),
  new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }),
));
koerper.position.x = 2.5;
scene.add(koerper);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const licht = new THREE.DirectionalLight(0xffffff, 2.5);
licht.position.set(3, 4, 5);
scene.add(licht);

function groesse() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  koerper.position.x = w < 700 ? 0 : 2.5;
}
window.addEventListener("resize", groesse);
groesse();

renderer.setAnimationLoop((t) => {
  koerper.rotation.x = t * 0.0002;
  koerper.rotation.y = t * 0.0003;
  renderer.render(scene, camera);
});
