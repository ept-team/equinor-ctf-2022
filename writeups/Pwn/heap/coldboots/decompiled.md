# Pwn / heap

## Complete decompile of the interesting bits

```c
void printMenu(void)
{
  puts("1. Malloc new heap chunk");
  puts("2. Write to chunk");
  puts("3. Free chunk");
  puts("4. View chunk");
  puts("5. Exit");
  return;
}

int getIdx(void)
{
  int idx;
  
  idx = readNum("index: ");
  if ((1 < idx) || (idx < 0)) {
    puts("out of range.");
    idx = 0;
  }
  return idx;
}

void create(void)
{
  int iVar1;
  void *pvVar2;
  
  iVar1 = getIdx();
  pvVar2 = malloc(0x10);
  *(void **)(listOfThings + (long)iVar1 * 8) = pvVar2;
  return;
}

void edit(void)
{
  int iVar1;
  
  iVar1 = getIdx();
  if (*(long *)(listOfThings + (long)iVar1 * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    printf("%s","value: ");
    fgets(*(char **)(listOfThings + (long)iVar1 * 8),0x10,stdin);
  }
  return;
}

void delete(void)
{
  int iVar1;
  
  iVar1 = getIdx();
  if (*(long *)(listOfThings + (long)iVar1 * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    free(*(void **)(listOfThings + (long)iVar1 * 8));
  }
  return;
}

void view(void)
{
  int iVar1;
  
  iVar1 = getIdx();
  if (*(long *)(listOfThings + (long)iVar1 * 8) == 0) {
    puts("index does not exist.");
  }
  else {
    puts(*(char **)(listOfThings + (long)iVar1 * 8));
  }
  return;
}

void leak(void)
{
  printf("%ld\n",free);
  return;
}

undefined8 main(void)
{
  undefined4 uVar1;
  
  ignore_me_init_buffering();
  ignore_me_init_signal();
  do {
    printMenu();
    uVar1 = readNum("> ");
    switch(uVar1) {
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
                    /* WARNING: Subroutine does not return */
      exit(1);
    case 6:
      leak();
    }
  } while( true );
}

```

