import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react';
import * as THREE from 'three';
import { normalizeTrace, type TracePoint } from './traceTypes';

function currentPoint(points: TracePoint[], index: number): TracePoint | null {
  if (points.length === 0) {
    return null;
  }

  return points[Math.max(0, Math.min(index, points.length - 1))];
}

function applyPhysicsPointToThreeObject(object: THREE.Object3D, point: TracePoint) {
  // ProtoForge / PyBullet trace uses Z as vertical.
  // Three.js uses Y as vertical.
  // Map physics: x -> three.x, y -> three.z, z -> three.y.
  object.position.set(point.x, point.z, point.y);
}

export function CubeTraceReplay({ rawTrace }: { rawTrace: unknown }) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const cubeRef = useRef<THREE.Group | null>(null);
  const frameRef = useRef<number | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const points = useMemo(() => normalizeTrace(rawTrace), [rawTrace]);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const point = currentPoint(points, index);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) {
      return undefined;
    }

    mount.innerHTML = '';
    setRenderError(null);

    let renderer: THREE.WebGLRenderer | null = null;
    let cubeGeometry: THREE.BoxGeometry | null = null;
    let edgeGeometry: THREE.EdgesGeometry | null = null;
    let cubeMaterial: THREE.MeshBasicMaterial | null = null;
    let edgeMaterial: THREE.LineBasicMaterial | null = null;

    try {
      const width = Math.max(mount.clientWidth, 420);
      const height = 300;

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x08111c);

      const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
      camera.position.set(4.5, 3.2, 6.0);
      camera.lookAt(0, 1.0, 0);

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      mount.appendChild(renderer.domElement);

      const grid = new THREE.GridHelper(6, 12, 0x00ccf0, 0x1e3248);
      grid.position.y = 0;
      scene.add(grid);

      const axes = new THREE.AxesHelper(2.25);
      scene.add(axes);

      cubeGeometry = new THREE.BoxGeometry(0.75, 0.75, 0.75);
      cubeMaterial = new THREE.MeshBasicMaterial({ color: 0x00ccf0 });
      const cubeMesh = new THREE.Mesh(cubeGeometry, cubeMaterial);

      edgeGeometry = new THREE.EdgesGeometry(cubeGeometry);
      edgeMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 2 });
      const cubeEdges = new THREE.LineSegments(edgeGeometry, edgeMaterial);

      const cubeGroup = new THREE.Group();
      cubeGroup.add(cubeMesh);
      cubeGroup.add(cubeEdges);
      cubeGroup.position.set(0, 2, 0);
      scene.add(cubeGroup);
      cubeRef.current = cubeGroup;

      const markerGeometry = new THREE.SphereGeometry(0.06, 16, 16);
      const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xf0a000 });
      const originMarker = new THREE.Mesh(markerGeometry, markerMaterial);
      originMarker.position.set(0, 0.06, 0);
      scene.add(originMarker);

      const animate = () => {
        renderer?.render(scene, camera);
        frameRef.current = requestAnimationFrame(animate);
      };

      animate();

      return () => {
        if (frameRef.current !== null) {
          cancelAnimationFrame(frameRef.current);
        }

        markerGeometry.dispose();
        markerMaterial.dispose();
        cubeGeometry?.dispose();
        edgeGeometry?.dispose();
        cubeMaterial?.dispose();
        edgeMaterial?.dispose();
        renderer?.dispose();
        mount.innerHTML = '';
        cubeRef.current = null;
      };
    } catch (error) {
      setRenderError(error instanceof Error ? error.message : String(error));
      return undefined;
    }
  }, []);

  useEffect(() => {
    if (!cubeRef.current || !point) {
      return;
    }

    applyPhysicsPointToThreeObject(cubeRef.current, point);
  }, [point]);

  useEffect(() => {
    if (!playing || points.length === 0) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      setIndex((value: number) => (value + 1 >= points.length ? 0 : value + 1));
    }, 45);

    return () => window.clearInterval(timer);
  }, [playing, points.length]);

  if (points.length === 0) {
    return (
      <div className="replay-placeholder">
        No normalized trace points available yet. The viewer is ready for verified state_trace.json.
      </div>
    );
  }

  return (
    <div className="trace-replay">
      <div className="trace-diagnostic">
        replay active · trace points: {points.length} · physics Z is mapped to Three.js Y
      </div>

      {renderError && (
        <div className="error-panel">
          Three.js renderer error: {renderError}
        </div>
      )}

      <div ref={mountRef} className="three-mount" />

      <div className="trace-controls">
        <button onClick={() => setPlaying((value: boolean) => !value)}>{playing ? 'Pause' : 'Play'}</button>
        <button onClick={() => { setPlaying(false); setIndex(0); }}>Reset</button>
        <input
          type="range"
          min={0}
          max={points.length - 1}
          value={index}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setPlaying(false);
            setIndex(Number(event.target.value));
          }}
        />
      </div>

      <div className="trace-readout">
        step {point?.step ?? 0} / {points.length - 1} · t={point?.t.toFixed(4) ?? '0'} ·
        physics x={point?.x.toFixed(3) ?? '0'} · physics y={point?.y.toFixed(3) ?? '0'} · physics z={point?.z.toFixed(3) ?? '0'}
      </div>
    </div>
  );
}
