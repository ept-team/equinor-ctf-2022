#pwn / :fire: thing :fire: full decompile

```c
undefined8 main(void)
{
  undefined4 choice;
  
  ignore_me_init_buffering();
  ignore_me_init_signal();
  disableSyscalls();
  do {
    printMenu();
    choice = readNum(&DAT_001020b7);
    switch(choice) {
    default:
      puts("out of range.");
      return 0;
    case 1:
      create();
      break;
    case 2:
      edit();
      break;
    case 3:
      delete();
      break;
    case 4:
      view();
      break;
    case 5:
      exit(1);
    }
  } while( true );
}

void disableSyscalls(void)
{
  undefined8 uVar1;
  
  uVar1 = seccomp_init(0x7fff0000);
  seccomp_rule_add(uVar1,0,322,0);
  seccomp_rule_add(uVar1,0,59,0);
  seccomp_rule_add(uVar1,0,57,0);
  seccomp_rule_add(uVar1,0,58,0);
  seccomp_load(uVar1);
  return;
}

void printMenu(void)
{
  puts("1. Create new thing");
  puts("2. Edit thing");
  puts("3. Delete thing");
  puts("4. Print thing");
  puts("5. Exit");
  return;
}

void readNum(long prompt)
{
  char *ret;
  long in_FS_OFFSET;
  char buff24 [24];
  long canary;
  
  canary = *(long *)(in_FS_OFFSET + 0x28);
  if (prompt != 0) {
    printf("%s",prompt);
  }
  ret = fgets(buff24,0xf,stdin);
  if (ret == (char *)0x0) {
    exit(-1);
  }
  ret = strchr(buff24,L'-');
  if (ret != (char *)0x0) {
    puts("out of range.");
    exit(1);
  }
  strtoull(buff24,(char **)0x0,0);
  if (canary != *(long *)(in_FS_OFFSET + 0x28)) {
    __stack_chk_fail();
  }
  return;
}

void create(void)
{
  int idx;
  void *mem;
  
  idx = getIdx();
  mem = malloc(0x10);
  *(void **)(listOfThings + (long)idx * 8) = mem;
  return;
}

int getIdx(void)
{
  int iVar1;
  
  iVar1 = readNum("index: ");
  if (111 < iVar1) {
    puts("out of range.");
    iVar1 = 0;
  }
  return iVar1;
}

void edit(void)
{
  int idx;
  
  idx = getIdx();
  if (*(long *)(listOfThings + (long)idx * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    printf("%s","value: ");
    fgets(*(char **)(listOfThings + (long)idx * 8),0x10,stdin);
  }
  return;
}

void delete(void)
{
  int idx;
  
  idx = getIdx();
  if (*(long *)(listOfThings + (long)idx * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    free(*(void **)(listOfThings + (long)idx * 8));
    *(undefined8 *)(listOfThings + (long)idx * 8) = 0;
  }
  return;
}

void view(void)
{
  int idx;
  
  idx = getIdx();
  if (*(long *)(listOfThings + (long)idx * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    puts(*(char **)(listOfThings + (long)idx * 8));
  }
  return;
}

```

